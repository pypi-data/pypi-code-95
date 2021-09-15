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
__date__ = "14/05/2020"

import logging

import numpy
from sklearn.decomposition import PCA

from darfix.decomposition.ipca import IPCA
from .base import Base

_logger = logging.getLogger(__file__)


class NICA(Base):
    """Compute the non-negative independent components of the linear generative
    model x = A * s.

    Here, x is a p-dimensional observable random vector and s is the latent
    random vector of length num_components, whose components are statistically
    independent and non-negative. The matrix X is assumed to hold n samples
    of x, stacked in rows (shape(X) = (n, p)) or columns (shape(X) = (p, n)),
    which can be specified by the rowvar parameter. In practice, if
    shape(X) = (p, n) (resp. shape(X) = (n, p)) this function solves X = A * S
    (resp. X = S.T * A.T) both for S and A, where A is the so-called mixing
    matrix, with shape (p, num_components), and S is a (num_components, n)
    matrix which contains n samples of the latent source vector, stacked in
    columns.

    This function implements the method presented in:
    `Blind Separation of Positive Sources by Globally Convergent Gradient Search`
    (https://core.ac.uk/download/pdf/76988305.pdf)

    :param data: array of shape (nsamples, nfeatures).
    :param num_components: Dimension of s. Number of latent random variables.
    :param chunksize: Size of every group of samples to apply PCA to. PCA will be fit with arrays
        of shape (chunksize, nfeatures), where nfeatures is the number of features per sample.
    :type chunksize: int
    :param float lr: Learning rate of gradient descent.
    :param int max_iter: Maximum number of iterations of gradient descent.
    :param float tol: Tolerance on update at each iteration.
    :type num_components: Union[uint, None]

    :return: (S, A) if rowvar == True else (S.T, A)

    """

    def __init__(self, data, num_components, chunksize=None, lr=0.03, indices=None):
        Base.__init__(self, data, num_components=num_components, indices=indices)

        self.lr = lr

        _logger.info("Whitening with PCA")
        # Whitening
        if chunksize is None:
            model = PCA(num_components, whiten=True)
            if indices is not None:
                self._Z = model.fit_transform(self.data[self.indices].T).T
            else:
                self._Z = model.fit_transform(self.data[:, :].T).T
            self._V = model.components_
        else:
            ipca = IPCA(self.data, chunksize, num_components, whiten=True, indices=indices, rowvar=False)
            ipca.fit_transform()
            self._Z = ipca.W.T
            self._V = ipca.H

        if self.num_components > self.Z.shape[0]:
            self.num_components = self.Z.shape[0]

    @property
    def Z(self):
        return self._Z

    @property
    def V(self):
        return self._V

    def _init_w(self):
        self.W = numpy.eye(self.num_components)

    def _update_w(self):
        """
        Apply NICA algorithm
        """
        Y = numpy.matmul(self.W, self.Z)

        f = numpy.minimum(0, Y)
        f_Y = numpy.matmul(f, Y.transpose())
        E = (f_Y - f_Y.transpose()) / Y.shape[1]
        # Gradient descent
        self.W -= self.lr * numpy.matmul(E, self.W)
        # Symmetric orthogonalization
        M = numpy.matmul(self.W, self.W.transpose())
        vals, vecs = numpy.linalg.eig(M)
        vals, vecs = vals.real, vecs.real

        W_sqrt = vecs / numpy.sqrt(vals)
        W_sqrt = numpy.matmul(W_sqrt, vecs.transpose())
        self.W = numpy.matmul(W_sqrt, self.W)

    def fit_transform(self, max_iter=100, error_step=None):

        _logger.info("Applying NICA algorithm")

        Base.fit_transform(self, max_iter=max_iter, error_step=error_step,
                           compute_h=False)

        self.H = numpy.matmul(self.W, self.Z)

        WV = numpy.matmul(self.W, self.V)
        WV_ = numpy.matmul(WV, WV.transpose())
        WV_ = numpy.linalg.inv(WV_)
        self.W = numpy.matmul(WV.transpose(), WV_)
