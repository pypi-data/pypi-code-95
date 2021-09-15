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

from sklearn.datasets import load_iris
from sklearn.decomposition import PCA

from darfix.decomposition.ipca import IPCA
from darfix.decomposition.nica import NICA
from darfix.decomposition.test.utils import images, sampler


class TestNICA(unittest.TestCase):
    """Tests for `nica.py`."""

    def setUp(self):
        iris = load_iris()
        self.X = iris.data

    def test_whiten_in_memory(self):
        nica = NICA(self.X, 2)
        pca = PCA(2, whiten=True)
        X = pca.fit_transform(self.X.T).T
        numpy.testing.assert_equal(X, nica.Z)
        numpy.testing.assert_equal(pca.components_, nica.V)

    def test_whiten_in_disk(self):
        nica = NICA(self.X, 2, chunksize=2)
        ipca = IPCA(self.X, 2, 2, whiten=True, rowvar=False)
        ipca.fit_transform()
        numpy.testing.assert_equal(ipca.W.T, nica.Z)
        numpy.testing.assert_equal(ipca.H, nica.V)

    def test_W(self):
        nica = NICA(self.X, 2)
        nica.fit_transform()
        self.assertEqual(nica.W.shape, (self.X.shape[0], 2))

    def test_H(self):
        nica = NICA(self.X, 2)
        nica.fit_transform()
        self.assertEqual(nica.H.shape, (2, self.X.shape[1]))

    def test_fit_transform(self):
        resources = ["circle", "star", "pentagon", "square"]
        num_images = 100
        means = [15, 30, 45, 60]
        tol = 0.7
        sample = sampler(resources, means)

        X = numpy.array([sample(i).flatten() for i in range(num_images)])
        nica = NICA(X, 4)
        nica.fit_transform(max_iter=1000)

        stack = numpy.asarray(images(resources))
        for img in stack:
            img = img / numpy.linalg.norm(img)
            found = False
            for component in nica.H:
                comp = component.reshape(img.shape)
                comp = comp / numpy.linalg.norm(comp)
                err = numpy.linalg.norm(comp - img)
                if err < tol:
                    found = True
                    break
            self.assertTrue(found)

    def test_fit_transform_IPCA(self):
        resources = ["circle", "star", "pentagon", "square"]
        num_images = 100
        means = [15, 30, 45, 60]
        tol = 0.7
        sample = sampler(resources, means)

        X = numpy.array([sample(i).flatten() for i in range(num_images)])
        nica = NICA(X, 4, chunksize=1000)
        nica.fit_transform(max_iter=1000)

        stack = numpy.asarray(images(resources))
        for img in stack:
            img = img / numpy.linalg.norm(img)
            found = False
            for component in nica.H:
                comp = component.reshape(img.shape)
                comp = comp / numpy.linalg.norm(comp)
                err = numpy.linalg.norm(comp - img)
                if err < tol:
                    found = True
                    break
            self.assertTrue(found)

    def test_fit_transform_indices(self):
        resources = ["circle", "star", "pentagon", "square"]
        num_images = 100
        means = [15, 30, 45, 60]
        tol = 0.7
        sample = sampler(resources, means)

        X = numpy.array([sample(i).flatten() for i in range(num_images)])
        nica = NICA(X, 4, indices=numpy.arange(50))
        nica.fit_transform(max_iter=1000)

        stack = numpy.asarray(images(resources[:-1]))
        for img in stack:
            img = img / numpy.linalg.norm(img)
            found = False
            for component in nica.H:
                comp = component.reshape(img.shape)
                comp = comp / numpy.linalg.norm(comp)
                err = numpy.linalg.norm(comp - img)
                if err < tol:
                    found = True
                    break
            self.assertTrue(found)

    def test_fit_transform_IPCA_indices(self):
        resources = ["circle", "star", "pentagon", "square"]
        num_images = 100
        means = [15, 30, 45, 60]
        tol = 0.7
        sample = sampler(resources, means)

        X = numpy.array([sample(i).flatten() for i in range(num_images)])
        nica = NICA(X, 4, chunksize=1000, indices=numpy.arange(50))
        nica.fit_transform(max_iter=1000)

        stack = numpy.asarray(images(resources[:-1]))
        for img in stack:
            img = img / numpy.linalg.norm(img)
            found = False
            for component in nica.H:
                comp = component.reshape(img.shape)
                comp = comp / numpy.linalg.norm(comp)
                err = numpy.linalg.norm(comp - img)
                if err < tol:
                    found = True
                    break
            self.assertTrue(found)
