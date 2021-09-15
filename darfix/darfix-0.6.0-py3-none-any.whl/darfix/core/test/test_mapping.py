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
__date__ = "17/11/2020"

import unittest
import numpy

from darfix.core import mapping


class TestMapping(unittest.TestCase):

    """Tests for `mapping.py`"""

    def setUp(self):
        self.data = numpy.random.random(size=(3, 10, 10))

    def test_generator1(self):
        """ Tests the correct creation of a generator without moments"""

        g = mapping.generator(self.data)

        img, moment = next(g)
        self.assertEqual(moment, None)
        numpy.testing.assert_array_equal(img, self.data[:, 0, 0])

    def test_generator2(self):
        """ Tests the correct creation of a generator with moments"""

        moments = numpy.ones((3, 10, 10))
        g = mapping.generator(self.data, moments)

        img, moment = next(g)
        numpy.testing.assert_array_equal(moment, moments[:, 0, 0])
        numpy.testing.assert_array_equal(img, self.data[:, 0, 0])

    def test_fit_rocking_curve(self):
        """ Tests the correct fit of a rocking curve"""

        samples = numpy.random.normal(size=10000) + numpy.random.random(10000)

        y, bins = numpy.histogram(samples, bins=100)

        y_pred = mapping.fit_rocking_curve([y, None])
        rss = numpy.sum((y - y_pred)**2)
        tss = numpy.sum((y - y.mean())**2)
        r2 = 1 - rss / tss

        self.assertGreater(r2, 0.9)

    def test_fit_data(self):
        """ Tests the new data has same shape as initial data"""

        new_data = mapping.fit_data(self.data)

        self.assertEqual(new_data.shape, self.data.shape)
