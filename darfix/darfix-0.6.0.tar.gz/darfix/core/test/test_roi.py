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
__date__ = "06/12/2019"


import unittest

import numpy

from darfix.core import roi


class TestROI(unittest.TestCase):

    """Tests for `roi.py`."""

    @classmethod
    def setUpClass(cls):

        cls.data = numpy.array([[[1, 2, 3, 4, 5], [2, 2, 3, 4, 5], [3, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
                                [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 3],
                                 [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
                                [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5],
                                 [8, 2, 3, 4, 5], [1, 2, 3, 4, 5]]])

        cls.dark = [[[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5],
                     [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
                    [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5],
                     [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
                    [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5],
                     [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]]]

    def test_ROI_0(self):
        """ Tests the roi of an image. """

        expected = numpy.array([[2, 3, 4], [2, 3, 4], [2, 3, 4]])

        data = roi.apply_2D_ROI(self.data[0], size=[3, 3], center=numpy.array(self.data[0].shape) / 2)
        numpy.testing.assert_equal(data, expected)

    def test_ROI_1(self):
        """ Tests the roi of an image. """

        expected = numpy.array([[1, 2], [2, 2]])

        data = roi.apply_2D_ROI(self.data[0], size=[3, 3], center=[0, 0])
        numpy.testing.assert_equal(data, expected)

    def test_ROI_2(self):
        """ Tests the roi of an image. """

        expected = numpy.array([[2, 3, 4, 5], [2, 3, 4, 5], [2, 3, 4, 5], [2, 3, 4, 5]])

        data = roi.apply_2D_ROI(self.data[0], size=[4, 4], center=[2, 3])
        numpy.testing.assert_equal(data, expected)

    def test_ROI_3D_0(self):
        """ Tests the roi of an image. """

        expected = numpy.array([[[1, 2], [2, 2]],
                                [[1, 2], [1, 2]],
                                [[1, 2], [1, 2]]])

        data = roi.apply_3D_ROI(self.data, size=[2, 2], origin=[0, 0])
        numpy.testing.assert_equal(data, expected)

    def test_ROI_3D_1(self):
        """ Tests the roi of an image. """

        expected = numpy.array([[[1]],
                                [[1]],
                                [[1]]])

        data = roi.apply_3D_ROI(self.data, size=[2, 2], center=[0, 0])
        numpy.testing.assert_equal(data, expected)

    def test_ROI_3D_2(self):
        """ Tests the roi of an image. """

        expected = numpy.array([[[2, 3, 4, 5], [2, 3, 4, 5], [2, 3, 4, 5], [2, 3, 4, 5]],
                               [[2, 3, 4, 5], [2, 3, 4, 5], [2, 3, 4, 3], [2, 3, 4, 5]],
                               [[2, 3, 4, 5], [2, 3, 4, 5], [2, 3, 4, 5], [2, 3, 4, 5]]])

        data = roi.apply_3D_ROI(self.data, size=[4, 4], center=[2, 3])
        numpy.testing.assert_equal(data, expected)


if __name__ == '__main__':
    unittest.main()
