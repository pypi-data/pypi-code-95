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
__date__ = "28/04/2020"

import numpy
import unittest

from darfix.decomposition.test.utils import images, sampler
from darfix.decomposition.nmf import NMF


class TestNMF(unittest.TestCase):
    """Tests for `nmf.py`."""

    def setUp(self):
        self.images = numpy.random.random((100, 1000))

    def test_fit_transform(self):
        resources = ["circle", "star", "pentagon", "square"]
        num_images = 100
        means = [15, 30, 45, 60]
        tol = 0.5
        sample = sampler(resources, means)

        X = numpy.array([sample(i).flatten() for i in range(num_images)])
        nmf = NMF(X, 4)
        nmf.fit_transform(max_iter=500)

        stack = numpy.asarray(images(resources))
        for img in stack:
            img = img / numpy.linalg.norm(img)
            found = False
            for component in nmf.H:
                comp = component.reshape(img.shape)
                comp = comp / numpy.linalg.norm(comp)
                err = numpy.linalg.norm(comp - img)
                if err < tol:
                    found = True
                    break
            self.assertTrue(found)
