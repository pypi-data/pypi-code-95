
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
from sklearn.preprocessing import StandardScaler

from nystrompca.base import KernelMachine, Transformation
from nystrompca.utils import (get_eigendecomposition, get_kappa,
                              IdentityScaler, demean_matrix, flip_dimensions)


class KernelPCA(KernelMachine, Transformation):

    """
    Kernel PCA.

    Parameters
    ----------
    scale : bool, default=True
        Whether to scale the input data to zero mean and unit variance

    Attributes
    ----------
    explained_variance_ : numpy.ndarray, 1d
        The variances of data along the principal components. Created
        in the 'fit_transform' method.

    components_ : numpy.ndarray, 2d
        The principal components, in terms of weightings on the m
        data points, with one principal component in each column
        of the array. Created in the 'fit_transform' method.

    errors_ : numpy.ndarray, 1d
        Reconstruction error of the full dataset on the principal
        components. Each element in the array is the reconstruction error
        with respect to all principal components up to that index.
        Calculated in the 'calculate_errors' method.

    """
    def __init__(self, scale:  bool = True,
                       demean: bool = True,
                       **kwargs           ):

        super().__init__(**kwargs)

        if scale:
            self.scaler = StandardScaler()
        else:
            self.scaler = IdentityScaler()

        self.demean = demean

        self.explained_variance_ = None
        self.all_variances       = None
        self.components_         = None
        self.errors_             = None
        self.n                   = None
        self.K_p                 = None


    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate the Kernel PCA for the supplied data matrix.

        Calculates the principal components, scores and values
        (explained variance).

        """
        n = X.shape[0]

        if self.n_components is None:
            self.n_components = n

        X = self.scaler.fit_transform(X)

        K_p  = self.kernel.matrix(X)
        print('kernel_PCA', self.demean)
        if self.demean:
            K_p = demean_matrix(K_p)
        L, Q = get_eigendecomposition(K_p / n)

        explained_variance_ = L[:self.n_components]

        Lambda = np.diag(n * explained_variance_)

        Q = Q[:,:self.n_components]
        scores_ = Q @ np.sqrt(Lambda)

        scores_, Q = flip_dimensions(scores_, Q)

        # Save calculated variables
        self.X                   = X
        self.n                   = n
        self.K_p                 = K_p
        self.scores_             = scores_
        self.explained_variance_ = explained_variance_
        self.Q                   = Q

        return self.scores_


    def transform(self, X_new: np.ndarray) -> np.ndarray:
        """
        Transform data into the coordinate system defined by the
        principal components including demeaning the data.

        Raises
        ------
        ValueError
            If the 'fit_transform' method has not been called yet

        """
        if self.scores_ is None:
            raise ValueError("Call 'fit_transform' before this function.")

        X_new = self.scaler.transform(X_new)

        n_new = X_new.shape[0]

        kappa = self.kernel.matrix(self.X, X_new)
        kappa_p = get_kappa(kappa, self.K)

        j = np.where(self.explained_variance_ > 0)[0][-1]
        Lambda_inv = np.diag(1 / (self.n * self.explained_variance_[:j+1]))

        X_transformed = kappa_p.T @ self.Q[:,:j+1] @ np.sqrt(Lambda_inv)

        # Add zeros for dimensions with zero explained variance
        X_transformed = np.c_[X_transformed, np.zeros((n_new, self.n_components-(j+1)))]

        return X_transformed

