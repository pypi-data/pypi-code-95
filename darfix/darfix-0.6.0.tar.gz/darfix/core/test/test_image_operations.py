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


import unittest

import numpy

from darfix.core import imageOperations


class TestImageOperations(unittest.TestCase):

    """Tests for `imageOperations.py`."""

    @classmethod
    def setUpClass(cls):

        cls.data = numpy.array([[[1, 2, 3, 4, 5],
                                 [2, 2, 3, 4, 5],
                                 [3, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5]],
                                [[1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 3],
                                 [1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5]],
                                [[1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5],
                                 [8, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5]]])

        cls.dark = numpy.array([[[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
                                [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
                                [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]]])

    def test_background_subtraction(self):
        """ Tests background subtraction function"""
        expected = numpy.array([[[0, 0, 0, 0, 0], [1, 0, 0, 0, 0], [2, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
                                [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
                                [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
                                 [7, 0, 0, 0, 0], [0, 0, 0, 0, 0]]])

        data = imageOperations.background_subtraction(self.data, self.dark)
        numpy.testing.assert_array_equal(expected, data)

    def test_im2img_mean(self):
        """ Tests img2img_mean function"""
        bg = None
        for i in range(self.dark.shape[0]):
            bg = imageOperations.img2img_mean(self.dark[i], bg, i)

        numpy.testing.assert_array_almost_equal(self.dark[0], bg)

    def test_chunk_image(self):
        """ Tests chunk_image function"""
        start = [0, 0]

        chunk_shape = [0, 0]

        img = imageOperations.chunk_image(start, chunk_shape, self.data[0])

        self.assertEqual(0, img.size)

        chunk_shape = [2, 2]

        img = imageOperations.chunk_image(start, chunk_shape, self.data[0])

        numpy.testing.assert_array_equal(self.data[0, :2, :2], img)

    def test_n_sphere_mask(self):
        """ Tests the creation of a mask from a 3d array. """

        expected = numpy.array([[[False, False, False, False, False],
                                 [False, True, True, True, False],
                                 [False, True, True, True, False],
                                 [False, True, True, True, False],
                                 [False, False, False, False, False]],
                                [[False, False, True, False, False],
                                 [False, True, True, True, False],
                                 [True, True, True, True, True],
                                 [False, True, True, True, False],
                                 [False, False, True, False, False]],
                                [[False, False, False, False, False],
                                 [False, True, True, True, False],
                                 [False, True, True, True, False],
                                 [False, True, True, True, False],
                                 [False, False, False, False, False]]])

        mask = imageOperations._create_n_sphere_mask(expected.shape, radius=2)

        numpy.testing.assert_array_equal(expected, mask)

    def test_circular_mask(self):
        """ Tests the correct creation of a circular mask"""
        expected = numpy.array([[False, False, True, False, False],
                                [False, True, True, True, False],
                                [True, True, True, True, True],
                                [False, True, True, True, False],
                                [False, False, True, False, False]])

        mask = imageOperations._create_circular_mask(expected.shape, radius=2)

        numpy.testing.assert_array_equal(expected, mask)

    def test_hot_pixel_removal(self):
        """ Tests the hot pixel removal in stack of arrays"""
        expected = numpy.array([[[1, 2, 3, 4, 5],
                                 [2, 2, 3, 4, 5],
                                 [2, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5]],
                                [[1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 4],
                                 [1, 2, 3, 4, 3],
                                 [1, 2, 3, 4, 4],
                                 [1, 2, 3, 4, 5]],
                                [[1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5],
                                 [2, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5]]], dtype=numpy.float32)

        data = imageOperations.hot_pixel_removal_3D(self.data)
        numpy.testing.assert_array_equal(expected, data)

    def test_threshold_removal(self):
        """ Tests the threshold of the data"""

        expected = numpy.array([[[1, 2, 3, 4, 0], [2, 2, 3, 4, 0], [3, 2, 3, 4, 0],
                                 [1, 2, 3, 4, 0], [1, 2, 3, 4, 0]],
                                [[1, 2, 3, 4, 0], [1, 2, 3, 4, 0], [1, 2, 3, 4, 3],
                                 [1, 2, 3, 4, 0], [1, 2, 3, 4, 0]],
                                [[1, 2, 3, 4, 0], [1, 2, 3, 4, 0], [1, 2, 3, 4, 0],
                                 [0, 2, 3, 4, 0], [1, 2, 3, 4, 0]]])

        data = imageOperations.threshold_removal(self.data, 1, 4)

        numpy.testing.assert_array_equal(expected, data)
