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
__date__ = "24/09/2020"


import numpy


def apply_2D_ROI(img, origin=None, size=None, center=None):
    """Function that computes a ROI at an image.

    :param array_like img: Image
    :param origin: Origin of the roi
    :param 2d-vector size: [Height, Width] of the roi.
    :param center: Center of the roi
    :type origin: Union[2d vector, None]
    :type center: Union[2d vector, None]
    :returns: ndarray
    :raises: AssertionError, ValueError
    """

    assert size is not None, "The size of the roi must be given"

    img = numpy.asanyarray(img)

    if origin is not None:
        assert all(i >= 0 for i in origin) \
            and all(j < img.shape[i] for i, j in enumerate(origin)), "Origin must be a valid pixel"
        origin = numpy.array(origin)
        size = numpy.array(size)
        points = numpy.ceil([origin, origin + size]).astype(numpy.int)
        points[1] = numpy.minimum(points[1], img.shape)
    elif center is not None:
        assert all(i >= 0 for i in center) \
            and all(j < img.shape[i] for i, j in enumerate(center)), "Center must be a valid pixel"
        center = numpy.array(center)
        size = numpy.array(size) * 0.5
        # Compute points and ceil in case of decimal
        points = numpy.ceil([center - size, center + size]).astype(numpy.int)
        # Check lower and upper bounds
        points[points < 0] = 0
        points[1] = numpy.minimum(points[1], img.shape)
    else:
        raise ValueError("Origin or center expected")
    return img[points[0, 0]:points[1, 0], points[0, 1]:points[1, 1]]


def apply_3D_ROI(data, origin=None, size=None, center=None):
    """Function that computes the ROI of each image in stack of images.

    :param array_like data: The stack of images
    :param origin: Origin of the roi
    :param 2d-vector size: [Height, Width] of the roi.
    :param center: Center of the roi
    :type origin: Union[2d vector, None]
    :type center: Union[2d vector, None]
    :returns: ndarray
    :raises: AssertionError, ValueError
    """
    assert size is not None, "The size of the roi must be given"

    data = numpy.asanyarray(data)

    if origin is not None:
        assert all(i >= 0 for i in origin) \
            and all(j < data[0].shape[i] for i, j in enumerate(origin)), "Origin must be a valid pixel"
        origin = numpy.array(origin)
        size = numpy.array(size)
        points = numpy.ceil([origin, origin + size]).astype(numpy.int)
        points[1] = numpy.minimum(points[1], data[0].shape)
    elif center is not None:
        assert all(i >= 0 for i in center) \
            and all(j < data[0].shape[i] for i, j in enumerate(center)), "Center must be a valid pixel"
        center = numpy.array(center)
        size = numpy.array(size) * 0.5
        # Compute points and ceil in case of decimal
        points = numpy.ceil([center - size, center + size]).astype(numpy.int)
        # Check lower and upper bounds
        points[points < 0] = 0
        points[1] = numpy.minimum(points[1], data[0].shape)
    else:
        raise ValueError("Origin or center expected")
    return data[:, points[0, 0]:points[1, 0], points[0, 1]:points[1, 1]]
