
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


"""
Calculation of confidence bound on empirical reconstruction error

"""

import numpy as np
from scipy.stats import norm

from nystrompca.utils import get_eigendecomposition


def calculate_bound(K_mm_p: np.ndarray,
                    n:      int,
                    B:      float,
                    alpha:  float     = 0.9) -> np.ndarray:
    """
    Calculation of confidence bound.

    Calculate a high-probability confidence bound on the empirical
    reconstruction error for kernel PCA with the Nyström method for
    all PCA dimensions.

    Parameters
    ----------
    L_m : numpy.ndarray, 1d
        Eigenvalues of the subset kernel matrix in decreasing order
    n : int
        Total size of dataset
    B: float
        maximum value of kernel function
    alpha: float
        confidence level

    Returns
    -------
    bounds : numpy.ndarray, 1d
        Confidence bound for all PCA dimensions

    """
    m = K_mm_p.shape[0]

    if m == n: # Zero error for the Nyström method
        return np.zeros(m)

    L_m, _ = get_eigendecomposition(K_mm_p / m)

    eig_diff = L_m[:-1] - L_m[1:]

    delta = np.log(2 / (1 - alpha))

    term1   = B * np.sqrt(2 * delta) / np.sqrt(n-m)
    term2_1 = np.sqrt(2 * np.log(2))
    term2_2 = 2 * np.sqrt(2 * np.pi) * norm.cdf(-np.sqrt(2*np.log(2)))
    term2   = B**2 / np.sqrt(m) * (term2_1 + term2_2)
    D = (n - m) / n * (term1 + term2)

    D_k = np.ones(len(eig_diff))
    non_zero = eig_diff > 1e-14
    D_k[non_zero] = D**2 / eig_diff[non_zero]**2
    D_k[D_k > 1] = 1

    max_D = np.array([np.max(D_k[:i+1]) for i in range(m-1)])

    bounds = np.cumsum(L_m[:-1] * D_k) + 0.5 * D * max_D

    # Add NaN for the last PCA dimension
    bounds = np.r_[bounds, np.nan]

    print("n: ", n)
    print("m: ", m)
    print("kernel sup: ", B)
    print("D: ", D)
    print("D_k: ", D_k)
    print("L_m: ", L_m)
    print("L sum: ", L_m.sum())
    print("terms: ", term1, " + ", term2)

    return bounds

