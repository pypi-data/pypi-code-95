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
__date__ = "22/04/2020"

import numpy
import unittest

from darfix.decomposition.base import Base


class TestBase(unittest.TestCase):
    """Tests for `base.py`."""

    def setUp(self):
        self.images = numpy.random.random((100, 1000))

    def test_data(self):
        base = Base(self.images)
        numpy.testing.assert_equal(self.images, base.data)

    def test_indices(self):
        base = Base(self.images)
        self.assertEqual(base.indices, None)

        base = Base(self.images, indices=numpy.arange(20))
        numpy.testing.assert_equal(base.indices, numpy.arange(20))

    def test_num_components(self):
        base = Base(self.images)
        self.assertEqual(base.num_components, 100)

        base = Base(self.images, num_components=10)
        self.assertEqual(base.num_components, 10)

    def test_W(self):
        base = Base(self.images, num_components=10)
        base.fit_transform()

        self.assertEqual(base.W.shape, (100, 10))

    def test_H(self):
        base = Base(self.images, num_components=10)
        base.fit_transform()

        self.assertEqual(base.H.shape, (10, 1000))

    def test_fit_transform(self):
        base = Base(self.images)
        base.fit_transform(compute_w=False)
        self.assertFalse(hasattr(base, 'W'))
        self.assertTrue(hasattr(base, 'H'))

        base = Base(self.images)
        base.fit_transform(compute_h=False)
        self.assertFalse(hasattr(base, 'H'))
        self.assertTrue(hasattr(base, 'W'))

    def test_frobenius_norm(self):
        base = Base(self.images)
        self.assertEqual(base.frobenius_norm(), None)

        base.fit_transform()
        self.assertNotEqual(base.frobenius_norm(), None)
