import os
import cv2 as cv
import numpy as np

def gaussian_2d(shape, centre, sigma=1.0):
    xs = np.arange(0.5, shape[1] + 0.5, step=1.0, dtype=np.float32)
    ys = np.expand_dims(np.arange(0.5, shape[0] + 0.5, step=1.0, dtype=np.float32), -1)
    alpha = -0.5 / (sigma**2)
    heatmap = np.exp(alpha * ((xs - centre[0])**2 + (ys - centre[1])**2))
    return heatmap


class Augment:
    def __init__(self, difficulty = 1.0, generate_heatmaps = False, heatmaps_scale = 1.0):
        self._generate_heatmaps = generate_heatmaps
        self._heatmaps_scale = heatmaps_scale
        self._difficulty = difficulty
        self._random_multipliers = []
        self._augmentation_ranges = {  # (easy, hard)
            'translation': (2.0, 10.0),
            'rotation': (0.1, 2.0),
            'intensity': (0.5, 20.0),
            'blur': (0.1, 1.0),
            'scale': (0.01, 0.1),
            'rescale': (1.0, 0.2),
            'num_line': (0.0, 2.0),
            'heatmap_sigma': (5.0, 2.5)
        }

    def set_difficulty(self, difficulty):
        assert isinstance(difficulty, float)
        assert 0.0 <= difficulty <= 1.0
        self._difficulty = difficulty

    def set_augmentation_range(self, augmentation_type, easy_value, hard_value):
        assert isinstance(augmentation_type, str)
        assert augmentation_type in self._augmentation_ranges
        assert isinstance(easy_value, float) or isinstance(easy_value, int)
        assert isinstance(hard_value, float) or isinstance(hard_value, int)
        self._augmentation_ranges[augmentation_type] = (easy_value, hard_value)

    def noisy_value_from_type (self, augmentation_type):
        val = np.random.uniform (*self._augmentation_ranges [augmentation_type])
        return np.clip (val * self._difficulty, *self._augmentation_ranges [augmentation_type])

    def __call__ (self, full_image):
        ih, iw = full_image.shape
        iw_2, ih_2 = 0.5 * iw, 0.5 * ih
        oh, ow = self._image_shape

        # Rotate eye image if requested
        rotate_mat = np.asmatrix(np.eye(3))
        rotation_noise = self.noisy_value_from_type('rotation')
        if rotation_noise > 0:
            rotate_angle = np.radians(rotation_noise)
            cos_rotate = np.cos(rotate_angle)
            sin_rotate = np.sin(rotate_angle)
            rotate_mat[0, 0] = cos_rotate
            rotate_mat[0, 1] = -sin_rotate
            rotate_mat[1, 0] = sin_rotate
            rotate_mat[1, 1] = cos_rotate

        # Scale image to fit output dimensions (with a little bit of noise)
        scale_mat = np.asmatrix(np.eye(3))
        scale = 1. + self.noisy_value_from_type('scale')
        scale_inv = 1. / scale
        np.fill_diagonal(scale_mat, ow * scale)

        # Re-centre eye image such that eye fits (based on determined `eye_middle`)
        recentre_mat = np.asmatrix(np.eye(3))
        recentre_mat[0, 2] += self.noisy_value_from_type('translation')  # x
        recentre_mat[1, 2] += self.noisy_value_from_type('translation')  # y

        # Apply transforms
        transform_mat = recentre_mat * scale_mat * rotate_mat * translate_mat
        pixels = cv.warpAffine(full_image, transform_mat[:2, :3], (ow, oh))

        # Draw line randomly
        num_line_noise = int(np.round(self.noisy_value_from_type('num_line')))
        if num_line_noise > 0:
            line_rand_nums = np.random.rand(5 * num_line_noise)
            for i in range(num_line_noise):
                j = 5 * i
                lx0, ly0 = int(ow * line_rand_nums[j]), oh
                lx1, ly1 = ow, int(oh * line_rand_nums[j + 1])
                direction = line_rand_nums[j + 2]
                if direction < 0.25:
                    lx1 = ly0 = 0
                elif direction < 0.5:
                    lx1 = 0
                elif direction < 0.75:
                    ly0 = 0
                line_colour = int(255 * line_rand_nums[j + 3])
                pixels = cv.line(pixels, (lx0, ly0), (lx1, ly1),
                              color=(line_colour, line_colour, line_colour),
                              thickness=max(1, int(6*line_rand_nums[j + 4])),
                              lineType=cv.LINE_AA)

        # Rescale image if required
        rescale_max = self.value_from_type('rescale')
        if rescale_max < 1.0:
            rescale_noise = np.random.uniform(low=rescale_max, high=1.0)
            interpolation = cv.INTER_CUBIC
            pixels = cv.resize(pixels, dsize=(0, 0), fx=rescale_noise, fy=rescale_noise,
                            interpolation=interpolation)
            pixels = cv.equalizeHist(pixels)
            pixels = cv.resize(pixels, dsize=(ow, oh), interpolation=interpolation)

        # Add rgb noise to eye image
        intensity_noise = int(self.value_from_type('intensity'))
        if intensity_noise > 0:
            pixels = pixels.astype(np.int16)
            pixels += np.random.randint(low=-intensity_noise, high=intensity_noise,
                                     size=pixels.shape, dtype=np.int16)
            cv.normalize(pixels, pixels, alpha=0, beta=255, norm_type=cv.NORM_MINMAX)
            pixels = pixels.astype(np.uint8)

        # Add blur to eye image
        blur_noise = self.noisy_value_from_type('blur')
        if blur_noise > 0:
            pixels = cv.GaussianBlur(pixels, (7, 7), 0.5 + np.abs(blur_noise))

        # Histogram equalization and preprocessing for NN
        pixels = cv.equalizeHist(pixels)
        pixels = pixels.astype(np.float32)
        pixels *= 2.0 / 255.0
        pixels -= 1.0
        pixels = np.expand_dims(pixels, -1 if self.data_format == 'NHWC' else 0)

        # Generate heatmaps if necessary
        if self._generate_heatmaps:
            # Should be half-scale (compared to eye image)
            entry['heatmaps'] = np.asarray([
                gaussian_2d(
                    shape=(self._heatmaps_scale*oh, self._heatmaps_scale*ow),
                    centre=self._heatmaps_scale*landmark,
                    sigma=value_from_type('heatmap_sigma'),
                )
                for landmark in entry['landmarks']
            ]).astype(np.float32)
            if self.data_format == 'NHWC':
                entry['heatmaps'] = np.transpose(entry['heatmaps'], (1, 2, 0))
        return entry
