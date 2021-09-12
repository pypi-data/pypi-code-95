
# Copyright 2020 Fredrik Hallgren
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import Optional

import numpy as np

from nystrompca import KernelPCA
from nystrompca.base import NystromMethod, Kernel
from nystrompca.utils import (get_inverse, demean_matrix, get_kappa,
                              get_eigendecomposition, flip_dimensions)


class NystromKPCA(KernelPCA, NystromMethod):

    """
    Nyström kernel PCA.

    """
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        print('nys init', self.demean)
        self.K_mm_p = None
        self.K_nm_p = None
        self.K_nm   = None
        self.K_p    = None


    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate the Nyström kernel PCA for the supplied data matrix.

        """
        self.n = X.shape[0]

        X = self.scaler.fit_transform(X)

        if self.n_components is None:
            self.n_components = self.n

        if self.subset is None:
            self.create_subset()
        print('nys fit', self.demean)
        K_mm_p, K_nm_p, K_nm = get_kernel_matrices(X, self.subset, self.kernel,
                                                   self.demean)

        K_inv_sqrt = get_inverse(K_mm_p, np.sqrt)

        nystrom_matrix = K_inv_sqrt @ K_nm_p.T @ K_nm_p @ K_inv_sqrt / self.n
        M, V = get_eigendecomposition(nystrom_matrix)

        components_ = K_inv_sqrt @ V[:,:self.n_components]
        scores_     = K_nm_p @ components_

        scores_, components_ = flip_dimensions(scores_, components_)

        self.all_variances       = M.copy() # TODO skip this (need to update experiments)
        self.explained_variance_ = M[:self.n_components]
        self.components_         = components_
        self.scores_             = scores_
        self.X                   = X
        self.K_mm_p              = K_mm_p
        self.K_nm_p              = K_nm_p
        self.K_nm                = K_nm

        return self.scores_


    def transform(self, X_new: np.ndarray) -> np.ndarray:
        """
        Transform data into the coordinate system defined by the
        approximate Nyström principal components

        Raises
        ------
        ValueError
            If the 'fit_transform' method has not been called yet

        """
        if self.components_ is None:
            raise ValueError("Call 'fit_transform' before this function.")

        X_new = self.scaler.transform(X_new)

        n_new = X_new.shape[0]

        kappa = self.kernel.matrix(self.X[self.subset], X_new)

        kappa_p = get_kappa(kappa, self.K_nm.T) # TODO use K_nm everywhere

        X_transformed = kappa_p.T @ self.components_

        return X_transformed


    def get_reconstruction_errors(self, X:      Optional[np.ndarray] = None,
                                        approx: bool                 = False
                                  ) -> np.ndarray:
        """
        Calculate the reconstruction errors of a dataset onto
        the Nyström principal components.

        This method requires contruction of the full kernel matrix,
        be mindful that this is compute intensive. There is an option
        to create an approximate error which takes O(nm^2).

        Parameters
        ----------
        X : None or numpy.ndarray, 2d
            Data matrix. If None then calculate the reconstruction error for
            the data used to fit the model
        approx : bool
            Whether to approximate the mean of the full kernel matrix
            Ignored if a new data matrix is supplied.

        Returns
        -------
        errors_ : numpy.ndarray
            Reconstruction errors

        Raises
        ------
        ValueError
            If the 'fit_transform' method has not been called yet

        """
        if self.components_ is None:
            raise ValueError("Call 'fit_transform' before this function.")

        if X is None:
            errors = self._get_reconstruction_error(approx)
        else:
            errors = self._get_reconstruction_error_new_data(X)

        return errors

    def _get_reconstruction_error(self, approx: bool) -> np.ndarray:
        """
        Calculate the reconstruction error *in feature space* of the training data set.

        """
        # TODO confirm this is in feature space ... should provide code for the
        # input space reconstruction error too!
        if not approx:
            if self.K_p is None:
                print('nystrom_KPCA', self.demean)
                self.K_p = self.kernel.matrix(self.X, demean=self.demean)
            tot_variance = np.trace(self.K_p) / self.n

        else:
            K_trace = [self.kernel(self.X[i], self.X[i]) for i in range(self.n)]
            row_means = self.K_nm.sum(1) / len(self.subset)
            full_mean = row_means.sum() / self.n
            tot_variance = np.sum(K_trace - 2 * row_means + full_mean) / self.n

        self.errors_ = tot_variance - np.cumsum(self.explained_variance_)

        return self.errors_


    # TODO seems this one is never used, so better to remove...
    def _get_reconstruction_error_new_data(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate the reconstruction error for new data using an existing
        PCA model.

        """
        n = X.shape[0]
        print('should not print')
        K_p = self.kernel.matrix(X, demean=self.demean)
        tot_variance = np.trace(K_p) / n

        X_transformed = self.transform(X)

        explained_variances = X_transformed.var(0)

        errors = tot_variance - np.cumsum(explained_variances)

        return errors


    def get_subset_errors(self) -> np.ndarray:
        """
        Calculate the reconstruction error of all n data points onto
        the eigenspace from the subset of m subsampled points

        Returns
        -------
        errors : numpy.ndarray
            Reconstruction errors for all PCA dimensions

        Raises
        ------
        ValueError
            If the 'fit_transform' method has not been called yet

        """
        if self.components_ is None:
            raise ValueError("Call 'fit_transform' before this function.")

        if self.K_p is None:
            print('subset errors', self.demean)
            self.K_p = self.kernel.matrix(self.X, self.X, demean=self.demean)

        L_m, U_m = get_eigendecomposition(self.K_mm_p)

        j = np.where(L_m > 0)[0][-1]

        projections = np.zeros(self.n_components)

        for i in range(self.n_components):

            k = min(i,j)
            L_k = np.diag(1 / L_m[:k+1])
            U_k = U_m[:,:k+1]
            mat = self.K_nm_p @ U_k @ L_k @ U_k.T @ self.K_nm_p.T
            projections[i] = np.trace(mat)

        errors = np.trace(self.K_p) / self.n - projections / self.n

        return errors


#############
### UTILS ###
#############

def get_kernel_matrices(X:      np.ndarray,
                        subset: np.ndarray,
                        kernel: Kernel    ,
                        demean: bool      ) -> (np.ndarray, np.ndarray):
    """
    Calculate the kernel matrices K_mm and K_nm

    Parameters
    ----------
    X: numpy.ndarray, 2d
        Data matrix
    subset: numpy.ndarray
        Subset indices
    kernel: nystrom_KPCA.kernel.Kernel
        Kernel wrapper class

    Returns
    -------
    K_mm_p : numpy.ndarray, 2d
        Centred kernel matrix with size m x m
    K_nm_p : numpy.ndarray, 2d
        Centred kernel matrix with size n x m
    K_nm : numpy.ndarray, 2d
        Kernel matrix with size n x m

    """
    K_nm = kernel.matrix(X, X[subset], demean=False)
    K_nm_p = K_nm.copy()

    K_mm_p = K_nm[subset]

    print('kernel_matrices', demean)
    if demean:
        K_nm_p = demean_matrix(K_nm)
        K_mm_p = demean_matrix(K_mm_p)

    return K_mm_p, K_nm_p, K_nm

