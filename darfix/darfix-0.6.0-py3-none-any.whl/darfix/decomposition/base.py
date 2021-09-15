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


import numpy
import scipy

from darfix.io import utils


class Base():
    """
    Base class for decomposition package.

    :param data: Numpy array or Hdf5 dataset with images in the rows and
        pixels in the columns.
    :param num_components: Number of components to keep, defaults to None
    :type num_components: Union[None,int], optional
    :param indices: The indices of the values to use, defaults to None
    :type indices: Union[None,array_like], optional
    :param epsilon: Convergence tolerance, defaults to 1e-07
    :type epsilon: float
    """

    def __init__(self, data, num_components=None, indices=None, epsilon=1e-7):

        self._data = data
        self._epsilon = epsilon

        self._num_samples, self._num_features = self.data.shape
        if indices is not None:
            self._num_samples = len(indices)
        self._indices = sorted(indices) if indices is not None else None
        self._num_components = (num_components if num_components
                                else min(self.num_samples, self.num_features))

    @property
    def data(self):
        return self._data

    @property
    def indices(self):
        return self._indices

    @property
    def num_samples(self):
        return self._num_samples

    @property
    def num_features(self):
        return self._num_features

    @property
    def num_components(self):
        return self._num_components

    def _init_w(self):

        self.W = numpy.random.random((self.num_samples, self.num_components))

        """ Add small value for faster convergence with non-zero values"""
        self.W += 10**-4

    def _init_h(self):

        self.H = numpy.random.random((self.num_components, self.num_features))

        """ Add small value for faster convergence with non-zero values"""
        self.H += 10**-4

    def _update_h(self):

        pass

    def _update_w(self):

        pass

    def frobenius_norm(self):
        """ Frobenius norm (||data - WH||) of a data matrix and a low rank
        approximation given by WH. Minimizing the Fnorm is the most common
        optimization criterion for matrix factorization methods.
        Returns:
        -------
        frobenius norm: F = ||data - WH||
        """
        # check if W and H exist
        if hasattr(self, 'H') and hasattr(self, 'W'):
            if scipy.sparse.issparse(self.data):
                tmp = self.data[:, :] - (self.W * self.H)
                tmp = tmp.multiply(tmp).sum()
                err = numpy.sqrt(tmp)
            else:
                err = numpy.sqrt(numpy.sum((self.data[:, :] - numpy.dot(self.W, self.H)) ** 2))
        else:
            err = None

        return err

    def _converged(self, i):
        """
        If the optimization of the approximation is below the machine precision,
        return True.
        :param int i: index of the update step

        :return: if converged
        :rtype: bool
        """
        derr = numpy.abs(self.ferr[i] - self.ferr[i - 1]) / self._num_samples
        if derr < self._epsilon:
            return True
        else:
            return False

    def fit_transform(self, max_iter=100, error_step=None, compute_w=True,
                      compute_h=True):
        """
        Fit to data, then transform it

        :param int max_iter: Maximum number of iterations, defaults to 100
        :type max_iter: int, optional
        :param error_step: If None, error is not computed, defaults to None
            Else compute error for every `error_step` images.
        :type error_step: Union[None,int], optional
        :param compute_w: When False, W is not computed, defaults to True
        :type compute_w: bool, optional
        :param compute_h: When False, H is not computed, defaults to True
        :type compute_h: bool, optional
        """

        self.ferr = []

        if compute_w:
            self._init_w()
        if compute_h:
            self._init_h()

        if max_iter > 1:
            utils.advancement_display(0, max_iter, "Updating decomposition matrices")

        for i in range(max_iter):

            if compute_w:
                self._update_w()
            if compute_h:
                self._update_h()

            if error_step:
                if not i % error_step:
                    self.ferr.append(self.frobenius_norm())
                    if i > error_step and self._converged(int(i / error_step)):
                        self.ferr = self.ferr[:i]
                        break
            if max_iter > 1:
                utils.advancement_display(i + 1, max_iter, "Updating decomposition matrices")
