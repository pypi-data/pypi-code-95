import numpy as np
from skimage.measure import compare_ssim as ssim
from math import log10, sqrt

# structural similarity index measure (SSIM)


def SSIM(predicted_image, target_image):
    """
    calculate Structural Similarity Index (SSIM) between two 3 Colored Channel/Grayscale images.

    :param predicted_image: Image Data for predicted image as numpy array
    :type predicted_image: np.array
    :param target_image: Image Data for target image as numpy array
    :type target_image: np.array
    :returns: SSIM SCORE  which calculated between the two input images.

    """

    score = 0

    # check image dimensions
    if predicted_image.ndim == target_image.ndim:
        if predicted_image.ndim == 4:
            predicted_image = np.squeeze(predicted_image, axis=0)
            target_image = np.squeeze(target_image, axis=0)

        # calculate for multichannel images
        if predicted_image.ndim > 1:
            score = ssim(predicted_image, target_image, multichannel=True)
        if predicted_image.ndim == 1:
            score = ssim(predicted_image, target_image, multichannel=False)
    return score


# Peak signal-to-noise ratio (PSNR)
def PSNR(predicted_image, target_image):
    """
    calculate Peak Signal-to-Noise Ratio (PSNR) between two 3 Colored Channel/Grayscale images.

    :param predicted_image: Image Data for predicted image as numpy array
    :type predicted_image: np.array
    :param target_image: Image Data for target image as numpy array
    :type target_image: np.array
    :returns: PSNR SCORE  which calculated between the two input images.

    """
    psnr = 0

    if predicted_image.ndim == target_image.ndim:
        if predicted_image.ndim == 4:
            predicted_image = np.squeeze(predicted_image, axis=0)
            target_image = np.squeeze(target_image, axis=0)

        # calculate PSNR
        mse = np.mean((target_image - predicted_image) ** 2)
        if mse == 0:
            return 100
        max_pixel = 255.0
        psnr = 20 * log10(max_pixel / sqrt(mse))
    return psnr


# Mean Squared Error (MSE)
def MSE(predicted_image, target_image):
    """
    calculate Mean Squared Error (MSE) between two 3 Colored Channel/Grayscale images.

    :param predicted_image: Image Data for predicted image as numpy array
    :type predicted_image: np.array
    :param target_image: Image Data for target image as numpy array
    :type target_image: np.array
    :returns: MSE SCORE  which calculated between the two input images.

    """
    error = np.sum(
        (target_image.astype("float") - predicted_image.astype("float")) ** 2
    )
    error /= float(target_image.shape[0] * target_image.shape[1])

    # return the MSE
    return error


# Root Mean Squared Error (RMSE)
def RMSE(predicted_image, target_image):
    """
    calculate Root Mean Squared Error (RMSE) between two 3 Colored Channel/Grayscale images.

    :param predicted_image: Image Data for predicted image as numpy array
    :type predicted_image: np.array
    :param target_image: Image Data for target image as numpy array
    :type target_image: np.array
    :returns: RMSE SCORE  which calculated between the two input images.

    """
    error = np.sum(
        (target_image.astype("float") - predicted_image.astype("float")) ** 2
    )
    error /= float(target_image.shape[0] * target_image.shape[1])

    root_error = sqrt(error)
    # return the RMSE
    return root_error


# Intersection over Union (IoU)
def IoU(predicted_box, target_box):
    """
    calculate Intersection over Union (IoU) between Predicted Bounding-box & Target Bounding-box of objects in an image.

    :param predicted_box: Array containing predicted bounding box points [x1,x2,y1,y2]
    :type predicted_box: array
    :param target_box: Array containing target bounding box points [x1,x2,y1,y2]
    :type target_image: array
    :returns: IoU, Union and Intersection SCORES.

    """
    inter_box_top_left = [
        max(target_box[0], predicted_box[0]),
        max(target_box[1], predicted_box[1]),
    ]
    inter_box_bottom_right = [
        min(target_box[0] + target_box[2], predicted_box[0] + predicted_box[2]),
        min(target_box[1] + target_box[3], predicted_box[1] + predicted_box[3]),
    ]

    inter_box_width = inter_box_bottom_right[0] - inter_box_top_left[0]
    inter_box_height = inter_box_bottom_right[1] - inter_box_top_left[1]

    intersection = inter_box_width * inter_box_height
    union = (
        target_box[2] * target_box[3]
        + predicted_box[2] * predicted_box[3]
        - intersection
    )

    iou = intersection / union

    return iou, union, intersection


# Structural Dissimilarity (DSSIM)
def DSSIM(predicted_image, target_image):
    """
    calculate Structural Dissimilarity(DSSIM) between two 3 Colored Channel/Grayscale images.

    :param predicted_image: Image Data for predicted image as numpy array
    :type predicted_image: np.array
    :param target_image: Image Data for target image as numpy array
    :type target_image: np.array
    :returns: DSSIM SCORE  which calculated between the two input images.

    """
    dssim_score = 0
    score = 0

    # check image dimensions
    if predicted_image.ndim == target_image.ndim:
        if predicted_image.ndim == 4:
            predicted_image = np.squeeze(predicted_image, axis=0)
            target_image = np.squeeze(target_image, axis=0)

        # calculate for multichannel images
        if predicted_image.ndim > 1:
            score = ssim(predicted_image, target_image, multichannel=True)
        if predicted_image.ndim == 1:
            score = ssim(predicted_image, target_image, multichannel=False)

        dssim_score = (1 - score) / 2
    return dssim_score


# Signal to Reconstruction Error ratio (SRE)
def SRE(predicted_image, target_image):
    """

    calculate Signal to Reconstruction Error ratio (SRE) between two 3 Colored Channel/Grayscale images.

    :param predicted_image: Image Data for predicted image as numpy array
    :type predicted_image: np.array
    :param target_image: Image Data for target image as numpy array
    :type target_image: np.array
    :returns: SRE SCORE  which calculated between the two input images.

    .. note:: You'll need to install image_similarity_measures library
    """

    import image_similarity_measures as ism

    score = 0

    # check image dimensions
    if predicted_image.ndim == target_image.ndim:
        if predicted_image.ndim == 4:
            predicted_image = np.squeeze(predicted_image, axis=0)
            target_image = np.squeeze(target_image, axis=0)

        # calculate for multichannel images
        if predicted_image.ndim > 1:
            score = ism.sre(target_image, predicted_image)
        if predicted_image.ndim == 1:
            score = ism.sre(target_image, predicted_image)

    return score


# Feature-based similarity index (FSIM)
def FSIM(predicted_image, target_image):
    """
    calculate Feature-based similarity index (FSIM) between two 3 Colored Channel/Grayscale images.

    :param predicted_image: Image Data for predicted image as numpy array
    :type predicted_image: np.array
    :param target_image: Image Data for target image as numpy array
    :type target_image: np.array
    :returns: FSIM SCORE  which calculated between the two input images.

    .. note:: You'll need to install image_similarity_measures library
    """

    import image_similarity_measures as ism

    score = 0

    # check image dimensions
    if predicted_image.ndim == target_image.ndim:
        if predicted_image.ndim == 4:
            predicted_image = np.squeeze(predicted_image, axis=0)
            target_image = np.squeeze(target_image, axis=0)

        # calculate for multichannel images
        if predicted_image.ndim > 1:
            score = ism.fsim(target_image, predicted_image)
        if predicted_image.ndim == 1:
            score = ism.fsim(target_image, predicted_image)

    return score


# Information theoretic-based Statistic Similarity Measure (ISSM)
def ISSIM(predicted_image, target_image):
    """
    calculate Information theoretic-based Statistic Similarity Measure (ISSM) between two 3 Colored Channel/Grayscale images.

    :param predicted_image: Image Data for predicted image as numpy array
    :type predicted_image: np.array
    :param target_image: Image Data for target image as numpy array
    :type target_image: np.array
    :returns: ISSIM SCORE  which calculated between the two input images.

    .. note:: You'll need to install image_similarity_measures library
    """

    import image_similarity_measures as ism

    score = 0

    # check image dimensions
    if predicted_image.ndim == target_image.ndim:
        if predicted_image.ndim == 4:
            predicted_image = np.squeeze(predicted_image, axis=0)
            target_image = np.squeeze(target_image, axis=0)

        # calculate for multichannel images
        if predicted_image.ndim > 1:
            score = ism.issim(target_image, predicted_image)
        if predicted_image.ndim == 1:
            score = ism.issim(target_image, predicted_image)

    return score


# Spectral angle mapper (SAM)
def SAM(predicted_image, target_image):
    """
    calculate Spectral angle mapper (SAM) between two 3 Colored Channel/Grayscale images.

    :param predicted_image: Image Data for predicted image as numpy array
    :type predicted_image: np.array
    :param target_image: Image Data for target image as numpy array
    :type target_image: np.array
    :returns: SAM SCORE  which calculated between the two input images.

    .. note:: You'll need to install image_similarity_measures library
    """

    import image_similarity_measures as ism

    score = 0

    # check image dimensions
    if predicted_image.ndim == target_image.ndim:
        if predicted_image.ndim == 4:
            predicted_image = np.squeeze(predicted_image, axis=0)
            target_image = np.squeeze(target_image, axis=0)

        # calculate for multichannel images
        if predicted_image.ndim > 1:
            score = ism.sam(target_image, predicted_image)
        if predicted_image.ndim == 1:
            score = ism.sam(target_image, predicted_image)

    return score


# Universal image quality index (UIQ)
def UIQ(predicted_image, target_image):
    """
    calculate Universal image quality index (UIQ) between two 3 Colored Channel/Grayscale images.

    :param predicted_image: Image Data for predicted image as numpy array
    :type predicted_image: np.array
    :param target_image: Image Data for target image as numpy array
    :type target_image: np.array
    :returns: UIQ SCORE  which calculated between the two input images.

    .. note:: You'll need to install image_similarity_measures library
    """

    import image_similarity_measures as ism

    score = 0

    # check image dimensions
    if predicted_image.ndim == target_image.ndim:
        if predicted_image.ndim == 4:
            predicted_image = np.squeeze(predicted_image, axis=0)
            target_image = np.squeeze(target_image, axis=0)

        # calculate for multichannel images
        if predicted_image.ndim > 1:
            score = ism.uiq(target_image, predicted_image)
        if predicted_image.ndim == 1:
            score = ism.uiq(target_image, predicted_image)

    return score
