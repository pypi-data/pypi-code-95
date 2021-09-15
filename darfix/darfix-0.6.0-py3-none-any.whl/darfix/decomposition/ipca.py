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
__date__ = "13/05/2020"

import numpy
from sklearn.decomposition import IncrementalPCA

from darfix.io import utils
from .base import Base


class IPCA(Base):
    """
    Compute PCA in chunks, using the Incremental principal component analysis implementation
    in scikit-learn.
    To compute W, partially fits the rows in chunks (reduced number of images). Then, to
    compute H, applies dimensionality reduction for every chunk, and horizontally stacks
    the projection into H.

    :param data: array of shape (n_samples, n_features). See `rowvar`.
    :type data: array_like
    :param chunksize: Size of every group of samples to apply PCA to. PCA will be fit with arrays
        of shape (chunksize, n_features), where nfeatures is the number of features per sample.
        Depending on `rowvar`, the chunks will be from the rows or from the columns.
    :type chunksize: int
    :param num_components: Number of components to keep, defaults to None.
    :type num_components: Union[None,int], optional
    :param whiten: If True, whitening is applied to the components.
    :type whiten: bool, optional
    :param indices: The indices of the samples to use, defaults to None. If `rowvar` is
        False, corresponds to the indices of the features to use.
    :type indices: Union[None,array_like], optional
    :param rowvar: If rowvar is True (default), then each row represents a sample,
        with features in the columns. Otherwise, the relationship is transposed: each
        column represents a sample, while the rows contain features.
    :type rowvar: bool, optional
    """

    def __init__(self, data, chunksize, num_components=None, whiten=False, indices=None,
                 rowvar=True):
        Base.__init__(self, data, num_components=num_components, indices=indices)

        self._num_components = min(self._num_components, chunksize)

        self._chunksize = chunksize
        self._singular_values = None
        self._rowvar = rowvar
        self._ipca = IncrementalPCA(n_components=num_components, whiten=whiten)

    @property
    def singular_values(self):
        """
        The singular values corresponding to each of the selected components.

        :retuns: array, shape (n_components,)
        """
        return self._singular_values

    def _init_w(self):
        """
        Init W to None.
        """
        if self.W is None and self._rowvar:
            Base._init_w(self)
        elif not self._rowvar:
            self.W = numpy.random.random((self.num_features, self.num_components))

    def _init_h(self):
        if self.H is None and self._rowvar:
            Base._init_h(self)
        elif not self._rowvar:
            self.H = numpy.random.random((self.num_components, self.num_samples))

    def _update_h(self):
        """
        Matrix H is filled with the components of IPCA.
        """
        self.H = self._ipca.components_

    def _update_w(self):
        if self.indices is not None:
            if not self._rowvar:
                # Samples are in the columns
                # Partially fit every chunk
                utils.advancement_display(0, self.num_features, "Fitting data with IPCA")
                assert self._chunksize >= self.num_components, \
                    "Chunksize has to be bigger than number of components"
                for i in range(0, self.num_features, self._chunksize):
                    if self.data.shape[1] - i < self.num_components:
                        # If at the last iteration the number of samples is smaller than
                        # the number of components.
                        utils.advancement_display(self.num_features, self.num_features, "Fitting data with IPCA")
                        break
                    self._ipca.partial_fit(self.data[self.indices, i: i + self._chunksize].T)
                    utils.advancement_display(i + 1, self.num_features, "Fitting data with IPCA")
                utils.advancement_display(0, self.num_features, "Transforming data with IPCA")
                # Transform every chunk to get W
                for i in range(0, self.num_features, self._chunksize):
                    self.W[i: i + self._chunksize] = \
                        self._ipca.transform(self.data[self.indices, i: i + self._chunksize].T)
                    utils.advancement_display(i + 1, self.num_features, "Transforming data with IPCA")
            else:
                # Images are in the rows
                # Partially fit every chunk
                utils.advancement_display(0, len(self.indices), "Fitting data with IPCA")
                assert self._chunksize >= self.num_components, \
                    "Chunksize has to be bigger than number of components"
                for i in range(0, len(self.indices), self._chunksize):
                    indx = self.indices[i: i + self._chunksize]
                    if len(indx) < self.num_components:
                        # If at the last iteration the number of samples is smaller than
                        # the number of components.
                        utils.advancement_display(len(self.indices), len(self.indices), "Fitting data with IPCA")
                        break
                    self._ipca.partial_fit(self.data[indx])
                    utils.advancement_display(i + 1, len(self.indices), "Fitting data with IPCA")
                utils.advancement_display(0, len(self.indices), "Transforming data with IPCA")
                # Transform every chunk to get W
                for i in range(0, len(self.indices), self._chunksize):
                    indx = self.indices[i: i + self._chunksize]
                    self.W[i: i + self._chunksize] = \
                        self._ipca.transform(self.data[indx])
                    utils.advancement_display(i + 1, len(self.indices), "Transforming data with IPCA")
        else:
            if not self._rowvar:
                # Samples are in the columns
                # Partially fit every chunk
                utils.advancement_display(0, self.num_features, "Fitting data with IPCA")
                assert self._chunksize >= self.num_components, \
                    "Chunksize has to be bigger than number of components"
                for i in range(0, self.num_features, self._chunksize):
                    if self.data.shape[1] - i < self.num_components:
                        # If at the last iteration the number of samples is smaller than
                        # the number of components.
                        utils.advancement_display(self.num_features, self.num_features, "Fitting data with IPCA")
                        break
                    self._ipca.partial_fit(self.data[:, i: i + self._chunksize].T)
                    utils.advancement_display(i + 1, self.num_features, "Fitting data with IPCA")
                utils.advancement_display(0, self.num_features, "Transforming data with IPCA")
                # Transform every chunk to get W
                for i in range(0, self.num_features, self._chunksize):
                    self.W[i: i + self._chunksize] = \
                        self._ipca.transform(self.data[:, i: i + self._chunksize].T)
                    utils.advancement_display(i + 1, self.num_features, "Transforming data with IPCA")
            else:
                # Partially fit every chunk
                utils.advancement_display(0, self.num_samples, "Fitting data with IPCA")
                assert self._chunksize >= self.num_components, \
                    "Chunksize has to be bigger than number of components"
                for i in range(0, self.num_samples, self._chunksize):
                    if self.data.shape[0] - i < self.num_components:
                        # If at the last iteration the number of samples is smaller than
                        # the number of components.
                        utils.advancement_display(self.num_samples, self.num_samples, "Fitting data with IPCA")
                        break
                    self._ipca.partial_fit(self.data[i: i + self._chunksize])
                    utils.advancement_display(i + 1, self.num_samples, "Fitting data with IPCA")
                utils.advancement_display(0, self.num_features, "Transforming data with IPCA")
                # Transform every chunk to get W
                for i in range(0, self.num_samples, self._chunksize):
                    self.W[i: i + self._chunksize] = \
                        self._ipca.transform(self.data[i: i + self._chunksize])
                    utils.advancement_display(i + 1, self.num_samples, "Transforming data with IPCA")

        self._singular_values = self._ipca.singular_values_

    def fit_transform(self, max_iter=1, error_step=None, W=None, H=None):

        self.W = None
        self.H = None

        Base.fit_transform(self, max_iter=max_iter, error_step=error_step)
