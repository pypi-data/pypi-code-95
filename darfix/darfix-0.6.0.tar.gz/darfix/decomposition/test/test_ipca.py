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

import random

import numpy
import unittest

from scipy.stats import special_ortho_group

from darfix.decomposition.ipca import IPCA


class TestIPCA(unittest.TestCase):
    """Tests for `ipca.py`."""

    def test_singular_values(self):
        data = numpy.random.random((100, 1000))
        ipca = IPCA(data, 50, num_components=3)
        self.assertEqual(ipca.singular_values, None)
        ipca.fit_transform()
        self.assertEqual(len(ipca.singular_values), 3)

    def test_fit_transform(self):
        # Number of features (dimension of the sample space)
        n = 10
        # Number of samples
        k = 100000
        # Number of principal components (dimension of the affine subspace)
        r = 5

        # Build principal components
        V = numpy.eye(n)[:, random.sample(range(n), r)]  # Subset of the standard basis vectors
        R = special_ortho_group.rvs(n)  # Random rotation in R^n
        V = numpy.dot(R, V)  # Principal components
        mean = numpy.random.rand(n)  # Affine space translation

        # Build observations
        D = numpy.diag(range(r, 0, -1))**2  # Matrix of decreasing eigenvalues
        Z = numpy.random.normal(size=(k, r))  # Dimensionality-reduced samples
        Z = numpy.dot(Z, D)
        X = numpy.dot(Z, V.T) + mean  # Observations

        # Apply PCA to X to get Z, V
        ipca = IPCA(X, chunksize=10000, num_components=r)
        ipca.fit_transform()
        estimated_Z = ipca.W
        estimated_V = ipca.H.T

        numpy.testing.assert_allclose(numpy.abs(estimated_Z), numpy.abs(Z), rtol=0, atol=1)
        numpy.testing.assert_allclose(numpy.abs(estimated_V), numpy.abs(V), rtol=0, atol=1)

    def test_fit_transform_indices(self):
        # Number of features (dimension of the sample space)
        n = 10
        # Number of samples
        k = 100000
        # Indices
        indices = numpy.arange(50000)
        # Number of principal components (dimension of the affine subspace)
        r = 5

        # Build principal components
        V = numpy.eye(n)[:, random.sample(range(n), r)]  # Subset of the standard basis vectors
        R = special_ortho_group.rvs(n)  # Random rotation in R^n
        V = numpy.dot(R, V)  # Principal components
        mean = numpy.random.rand(n)  # Affine space translation

        # Build observations
        D = numpy.diag(range(r, 0, -1))**2  # Matrix of decreasing eigenvalues
        Z = numpy.random.normal(size=(k, r))  # Dimensionality-reduced samples
        Z = numpy.dot(Z, D)
        X = numpy.dot(Z, V.T) + mean  # Observations

        # Apply PCA to X to get Z, V
        ipca = IPCA(X, chunksize=10000, num_components=r, indices=indices)
        ipca.fit_transform()
        estimated_Z = ipca.W
        estimated_V = ipca.H.T

        numpy.testing.assert_allclose(numpy.abs(estimated_Z), numpy.abs(Z[indices]), rtol=0, atol=1)
        numpy.testing.assert_allclose(numpy.abs(estimated_V), numpy.abs(V), rtol=0, atol=1)
