# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/


__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "08/12/2020"

import numpy
import silx.math
from silx.utils.enum import Enum as _Enum


class Method(_Enum):
    """
    Methods available to compute the background.
    """
    mean = "mean"
    median = "median"


def background_subtraction(data, bg_frames, method='median'):

    """Function that computes the median between a series of dark images from a dataset
    and subtracts it to each frame of the raw data to remove the noise.

    :param ndarray data: The raw data
    :param array_like bg_frames: List of dark frames
    :param method: Method used to determine the background image.
    :type method: Union['mean', 'median', None]
    :returns: ndarray
    :raises: ValueError
    """
    assert bg_frames is not None, "Background frames must be given"
    background = numpy.zeros(data[0].shape, data.dtype)
    method = Method.from_value(method)
    if len(bg_frames):
        if method == Method.mean:
            numpy.mean(bg_frames, out=background, axis=0)
        elif method == Method.median:
            numpy.median(bg_frames, out=background, axis=0)
        else:
            raise ValueError("Invalid method specified. Please use `mean`, "
                             "or `median`.")
    if data.dtype.kind == 'i' or data.dtype.kind == 'u':
        new_data = numpy.subtract(data, background, dtype=numpy.int32)
    else:
        new_data = numpy.subtract(data, background)
    new_data[new_data < 0] = 0

    return new_data.astype(data.dtype)


def img2img_mean(img, mean=None, n=0):
    """
    Update mean from stack of images, given a new image and its index in
    the stack.

    :param array_like img: img to add to the mean
    :param array_like mean: mean img
    :param int n: index of the last image in the stack

    :return: Image with new mean
    """
    if not numpy.any(mean):
        mean = img
    else:
        mean = (mean * n + img) / (n + 1)

    return mean


def background_subtraction_2D(img, bg):
    """
    Compute background subtraction.

    :param array_like img: Raw image
    :param array_like bg: Background image

    :return: Image with subtracted background
    """
    if img.dtype.kind == 'i' or img.dtype.kind == 'u':
        img = numpy.subtract(img, bg.astype(img.dtype), dtype=numpy.int32)
    else:
        img = numpy.subtract(img, bg.astype(img.dtype))
    img[img < 0] = 0
    return img


def _create_circular_mask(shape, center=None, radius=None):
    """
    Function that given a height and a width returns a circular mask image.

    :param int h: Height
    :param int w: Width
    :param center: Center of the circle
    :type center: Union[[int, int], None]
    :param radius: Radius of the circle
    :type radius: Union[int, None]
    :returns: ndarray
    """
    h, w = shape
    if center is None:  # use the middle of the image
        center = [int(h / 2), int(w / 2)]
    if radius is None:  # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], h - center[0], w - center[1])

    X, Y = numpy.ogrid[:h, :w]
    dist_from_center = numpy.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)

    mask = dist_from_center <= radius
    return mask


def _create_n_sphere_mask(shape, center=None, radius=None):
    """
    Function that given a list of dimensions returns a n-dimensional sphere mask.

    :param shape: Dimensions of the mask
    :type shape: array_like
    :param center: Center of the sphere
    :type center: Union[array_like, None]
    :param radius: Radius of the sphere
    :type radius: Union[int, None]
    :returns: ndarray
    """

    assert shape or radius, "If dimensions are not entered radius must be given"

    dimensions = numpy.array(shape)

    if center is None:  # use the middle of the image
        center = (dimensions / 2).astype(int)
    if radius is None:  # use the smallest distance between the center and image walls
        radius = min(numpy.concatenate([center, dimensions - center]))

    C = numpy.ogrid[[slice(0, dim) for dim in dimensions]]
    dist_from_center = numpy.sqrt(numpy.sum((C - center) ** 2))

    mask = dist_from_center <= radius
    return mask


def chunk_image(start, chunk_shape, img):
    """
    Return a chunk of an image.

    :param array_like img: Raw image
    :param tuple start: Start of the chunk in the image
    :param tuple shape: Shape of the chunk
    """
    return img[start[0]: start[0] + chunk_shape[0], start[1]:start[1] + chunk_shape[1]]


def hot_pixel_removal_3D(data, ksize=3):
    """
    Function to remove hot pixels of the data using median filter.

    :param array_like data: Input data.
    :param int ksize: Size of the mask to apply.
    :returns: ndarray
    """
    corrected_data = numpy.empty(data.shape, dtype=data.dtype)
    for i, frame in enumerate(data):
        corrected_data[i] = hot_pixel_removal_2D(frame, ksize)
    return corrected_data


def hot_pixel_removal_2D(image, ksize=3):
    """
    Function to remove hot pixels of the data using median filter.

    :param array_like data: Input data.
    :param int ksize: Size of the mask to apply.
    :returns: ndarray
    """
    if image.dtype == numpy.int or image.dtype == numpy.uint:
        # Cast to int and not uint to later subtract
        image = image.astype(numpy.int16)
    elif image.dtype == numpy.float:
        image = image.astype(numpy.float32)
    corrected_image = numpy.array(image)
    median = silx.math.medfilt(corrected_image, ksize)
    if image.dtype.kind == 'i' or image.dtype.kind == 'u':
        hot_pixels = numpy.subtract(corrected_image, median, dtype=numpy.int32)
    else:
        hot_pixels = numpy.subtract(corrected_image, median)
    threshold = numpy.std(hot_pixels)
    corrected_image[hot_pixels > threshold] = median[hot_pixels > threshold]
    return corrected_image


def threshold_removal(data, bottom=None, top=None):
    """
    Set bottom and top threshold to the images in the dataset.

    :param Dataset dataset: Dataset with the data
    :param int bottom: Bottom threshold
    :param int top: Top threshold
    :returns: ndarray
    """

    new_data = numpy.array(data, dtype=data.dtype)
    if bottom is not None:
        new_data[new_data < bottom] = 0
    if top is not None:
        new_data[new_data > top] = 0

    return new_data
