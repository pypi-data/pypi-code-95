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
__date__ = "06/04/2020"

import logging

import numpy
from .base import Base

_logger = logging.getLogger(__file__)


class NMF(Base):
    """
    Non-Negative Matrix Factorization.

    Find two non-negative matrices whose product approximates the non-negative
    matrix data.
    """
    def _init_w(self):
        if self.W is None:
            Base._init_w(self)

    def _init_h(self):
        if self.H is None:
            Base._init_h(self)

    def _update_h(self):
        _logger.info("Updating H")

        H2 = numpy.empty(self.H.shape[0])
        h = numpy.empty(self.H.shape[1])
        for row in range(self.W.shape[1]):
            H2 = numpy.matmul(numpy.matmul(self.W.T[row], self.W), self.H) + 10**-9
            for column in range(0, self.H.shape[1], self._hstep):
                if self.indices is None:
                    h[column:column + self._hstep] = numpy.matmul(
                        self.W.T[row], self.data[:, column:column + self._hstep])
                else:
                    h[column:column + self._hstep] = numpy.matmul(
                        self.W.T[row], self.data[self.indices, column:column + self._hstep])
            self.H[row] *= h
            self.H[row] /= H2

    def _update_w(self):
        _logger.info("Updating W")

        W2 = numpy.empty(self.W.shape[0])
        if self.indices is None:
            for row in range(0, len(self.W), self._vstep):
                W2 = numpy.matmul(numpy.matmul(self.W[row:row + self._vstep], self.H), self.H.T) + 10**-9
                numpy.matmul(self.data[row:row + self._vstep], self.H.T)
                self.W[row:row + self._vstep] *= numpy.matmul(self.data[row:row + self._vstep], self.H.T)
                self.W[row:row + self._vstep] /= W2
        else:
            for row in range(0, len(self.indices), self._vstep):
                indx = self.indices[row:row + self._vstep]
                W2 = numpy.matmul(numpy.matmul(self.W[row:row + self._vstep], self.H), self.H.T) + 10**-9
                numpy.matmul(self.data[indx], self.H.T)
                self.W[row:row + self._vstep] *= numpy.matmul(self.data[indx], self.H.T)
                self.W[row:row + self._vstep] /= W2

        self.W /= numpy.sqrt(numpy.sum(self.W**2.0, axis=0))

    def fit_transform(self, H=None, W=None, max_iter=200, compute_w=True, compute_h=True,
                      vstep=100, hstep=1000, error_step=None):
        """
        Find the two non-negative matrices (H, W). The images are loaded from disk in chunks.

        :param H: If not None, used as initial guess for the solution.
        :type H: array_like, shape (n_components, n_features), optional
        :param W: If not None, used as initial guess for the solution.
        :type W: array_like, shape (n_samples, n_components)
        :param max_iter: Maximum number of iterations before timing out,
            defaults to 200
        :type max_iter: int, optional
        :param compute_w: If False, W is not computed.
        :type compute_w: bool, optional
        :param compute_h: If False, H is not computes.
        :type compute_h: bool, optional
        :param vstep: vertical size of the chunks to take from data.
            When updating W, `vstep` images are retrieved from disk per iteration,
            defaults to 100.
        :type vstep: int, optional
        :param hstep: horizontal size of the chunks to take from fata.
            When updating H, `hstep` pixels are retrieved from disk per iteration,
            defaults to 1000.
        :type hstep: int, optional
        :param error_step: If None, error is not computed, else compute error for
            every `error_step` images.
        :type error_step: Union[None,int], optional
        """

        self.H = H
        self.W = W
        self._vstep = vstep
        self._hstep = hstep

        _logger.info("Starting NMF algorithm")

        Base.fit_transform(self, max_iter=max_iter, error_step=error_step, compute_w=compute_w,
                           compute_h=compute_h)
