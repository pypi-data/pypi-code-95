import numpy as np
from PIL import Image

from uberlimb.parameters import PostFXParams, FrameColorMap
from uberlimb.post_fx.palette.brand_palette import PALETTE


class LimbFrame:
    def __init__(self, arr: np.ndarray):
        self._raw_arr = arr
        self.arr = arr

    def as_pillow(self) -> Image:
        img = Image.fromarray(self.arr.squeeze())
        return img

    def as_array(self):
        return self.arr

    def postprocess_binning(self, dither_strength: float, as_float=False):
        if not len(self._raw_arr.shape) == 3:
            raise ValueError('Expected 3-dim self._raw_arr')
        digitize_depth = 1000 if as_float else 255
        return_type = np.float32 if as_float else np.uint8
        result = np.zeros(self._raw_arr.shape, return_type)
        for idx in range(self._raw_arr.shape[-1]):
            arr = self._raw_arr[..., idx].ravel()
            arr = arr + (np.random.random(arr.size) - 0.5) * (dither_strength / 256)
            splits = np.array_split(np.sort(arr), digitize_depth * 2)
            cutoffs = [x[-1] for x in splits][:-1]
            discrete = np.digitize(arr, cutoffs, right=True)
            arr = discrete.reshape(*self._raw_arr.shape[:2])
            if as_float:
                arr = arr / (digitize_depth * 2)
            else:
                arr = np.abs(digitize_depth - arr % digitize_depth * 2)
            result[..., idx] = arr.squeeze()
        self.arr = result

    def apply_post_fx(self, params: PostFXParams):
        if params.color_map == FrameColorMap.BINNING:
            self.postprocess_binning(params.dither_strength)
        else:
            if params.flat_colors:
                self.postprocess_binning(params.dither_strength, as_float=True)
                self.apply_product_flat(params.color_map)
            else:
                self.postprocess_binning(params.dither_strength, as_float=True)
                self.apply_product(params.color_map)

    def apply_product(self, product_name: FrameColorMap):
        palette = PALETTE[product_name]
        xp = [0, 0.4, 0.7, 0.9, 1]
        red_color = np.interp(self.arr, xp, palette['r'])
        green_color = np.interp(self.arr, xp, palette['g'])
        blue_color = np.interp(self.arr, xp, palette['b'])
        self.arr = np.concatenate((red_color, green_color, blue_color),
                                  axis=-1).astype(np.uint8)

    def apply_product_flat(self, product_name: FrameColorMap):
        if not self.arr.shape[2] == 1:
            raise ValueError('Expected grayscale self.arr')
        palette = PALETTE[product_name]
        arr_max = self.arr.max()
        steps = [x * arr_max / 15 for x in range(16)]
        steps[-1] += 0.01
        new_arr = np.zeros((*self.arr.shape[:2], 3), np.uint8)
        for i in range(len(steps) - 1):
            pixel_mask = (steps[i] <= self.arr) * (self.arr < steps[i + 1])
            pixel_mask = pixel_mask.squeeze()
            color = np.array([palette['r'][i % (len(palette['r']) - 1)],
                              palette['g'][i % (len(palette['r']) - 1)],
                              palette['b'][i % (len(palette['r']) - 1)]])
            new_arr[pixel_mask, :] = color
        self.arr = new_arr
