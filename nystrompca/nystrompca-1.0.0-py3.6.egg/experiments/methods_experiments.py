
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
Experiments comparing Nyström kernel PCA with a range of other unsupervised
learning methods

* Linear PCA
* Kernel PCA
* Sparse PCA
* Robust PCA
* MDS
* Isomap
* LLE
* Autoencoder
* RBM
* ICA

As a measure of the accuracy we use the average
reconstruction errors of a hold-out data set.

"""

# Built-in modules
import sys
from multiprocessing import Pool, cpu_count

# Third-party packages
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA, SparsePCA, FastICA, DictionaryLearning
from sklearn.manifold import MDS, Isomap, LocallyLinearEmbedding

# This package
from nystrompca import KernelPCA, NystromKPCA
from nystrompca.algorithms.autoencoder import AutoEncoder
from nystrompca.experiments import base_parser, data
from nystrompca.utils import logger


# Always display numbers in decimal format, using 4 decimals
pd.options.display.float_format = '{:,.4f}'.format


def main(kernel:  str = "",
         n:       int = 1000,
         m:       int = 20,
         d:       int = 10,
         save:   bool = False) -> int:
    """
    Run the experiments.

    Calculates the reconstruction error

    Parameters
    ----------
    kernel: str
        Kernel function to use
    n : int
        Total size of dataset
    m : int
        Size of subsampled dataset
    d : int
        Maximum subspace dimension
    save : bool
        Whether to store the figures on disk

    Returns
    -------
    int
        Return code, 0 if success

    """
    logger.header("Methods comparison experiments")

    logger.info("Kernel: {}".format(kernel))
    logger.info("n: {}".format(n))
    logger.info("m: {}".format(m))

    all_results = pd.DataFrame()

    # TODO more datasets

    for dataset in ('digits', 'dailykos', 'nips', 'facebook'):
    #('magic', 'yeast', 'cardiotocography', 'segmentation',

        logger.subheader("Dataset: {}".format(dataset))

        X = getattr(data, "get_" + dataset + "_data")(n)

        results = run_one_dataset(kernel, X, m, d)
        logger.info("Results:")
        logger.info(results)

        results['dataset'] = dataset

        all_results = all_results.append(results)

    # Actually doesn't make sense to average across datasets. Just display everything,
    # But maybe do more spaced d values (like every 5 components)
    #all_results = all_results.groupby('d').mean()

    return 0


def run_one_dataset(kernel:  str,
                    X:       np.ndarray,
                    m:       int,
                    d:       int       ) -> pd.DataFrame:
    """
    Run an experiment for one kernel and dataset for all methods.

    Parameters
    ----------
    kernel : str
        Kernel function
    X : numpy.ndarray, 2d
        Data matrix, with observations in the rows
    m : int
        The size of the Nyström subset
    d : int
        Subspace dimension

    Returns
    -------
    results : pandas.DataFrame
        The results of one experiment

    """
    X_train, X_test = train_test_split(X, test_size=0.5)

    scaler  = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)

    results = pd.DataFrame()

    results['Nystrom PCA'] = run_nystrom_kpca(X_train, X_test, kernel, m, d)

    results['Kernel PCA']  = run_kernel_pca(X_train, X_test, kernel, d)

    results['Linear PCA']  = run_linear_pca(X_train, X_test, d)

    results['Sparse PCA']  = run_sparse_pca(X_train, X_test, d)

    results['LLE']         = run_lle(X_train, X_test, d)

    results['ICA']         = run_ica(X_train, X_test, d)



    # WIP
    #results['Autoencoder'] = run_autoencoder(X_train, X_test, d)


    # Q: is kernel PCA actually equivalent to MDS?
    # Seems so pretty much. Therefore I should write in the discussion
    # that the Nyström method can also be applied to MDS!

    # Made a new effort with isomap but maybe have to re-implement part
    # of the algorithm myself to make it work...
    #results['Isomap']      = run_isomap(X_train, X_test, d)

    # TODO Rewrite experiments so that we run for one dataset at a time? Or maybe not

    # Almost works, but not entirely sure how to normalize...
    #results['Dictionary']  = run_dictionary_learning(X_train, X_test, d)

    results['d'] = range(1,d+1)

    return results


def run_linear_pca(X_train: np.ndarray,
                   X_test:  np.ndarray,
                   d:       int       ) -> np.ndarray:

    explained_variances = np.zeros(d)

    d = min(d, X_train.shape[1])

    linear_pca = PCA(n_components=d)

    linear_pca.fit_transform(X_train)

    explained_variances[:d] = linear_pca.transform(X_test).var(0)

    total_variance = np.sum(X_test.var(0)) # Sum of variances across all dimensions

    explained_fractions = np.cumsum(explained_variances) / total_variance

    return explained_fractions


def run_sparse_pca(X_train: np.ndarray,
                   X_test:  np.ndarray,
                   d:       int       ) -> np.ndarray:

    explained_variances = np.zeros(d)
    explained_variances.fill(np.nan)

    if X_train.shape[1] > 25:
        return explained_variances

    d1 = min(d, X_train.shape[1])

    for i in range(d1):
        sparse_pca = SparsePCA(n_components=i+1)
        sparse_pca.fit_transform(X_train)
        explained_variances[i] = sparse_pca.transform(X_test).var(0).sum()

    total_variance = np.sum(X_test.var(0)) # Sum of variances across all dimensions

    explained_fractions = explained_variances / total_variance

    explained_fractions[np.isnan(explained_fractions)] = max(explained_fractions)

    return explained_fractions


def run_kernel_pca(X_train, X_test, kernel, d) -> float:
    """
    Calculate the reconstruction errors (in input space) for all PCA
    dimensions from 1 to d, returned in increasing order.

    """
    kernel_pca = KernelPCA(kernel=kernel, sigma=100, n_components=d)

    kernel_pca.fit_transform(X_train)

    explained_variances = kernel_pca.transform(X_test).var(0)

    K = kernel_pca.kernel.matrix(X_test, demean=True)

    total_variance = np.trace(K) / X_test.shape[0]

    explained_fractions = np.cumsum(explained_variances) / total_variance

    return explained_fractions


def run_nystrom_kpca(X_train, X_test, kernel, m, d) -> float:
    """
    Calculate the fraction of explained variances (in feature space) for all PCA
    dimensions from 1 to d, returned in increasing order.

    """
    explained_variances = np.zeros(d)

    nystrom_kpca = NystromKPCA(kernel=kernel, sigma=100, n_components=d, m_subset=m)

    nystrom_kpca.fit_transform(X_train)

    explained_variances0 = nystrom_kpca.transform(X_test).var(0)

    explained_variances[:len(explained_variances0)] = explained_variances0

    K = nystrom_kpca.kernel.matrix(X_test, demean=True)

    total_variance = np.trace(K) / X_test.shape[0]

    explained_fractions = np.cumsum(explained_variances) / total_variance

    return explained_fractions


def run_autoencoder(X_train, X_test, d):

    explained_variances = np.zeros(d)

    for i in range(d):
        autoenc = AutoEncoder(epochs=10, n_components=i+1)
        autoenc.fit_transform(X_train)
        explained_variances[i] = autoenc.transform(X_test).var(0).sum()

    total_variance = np.sum(X_test.var(0))

    explained_fractions = np.cumsum(explained_variances) / total_variance

    return explained_fractions


def run_lle(X_train, X_test, d):

    # I think we can do this one. Similarly to how we would do it with isomap,
    # we find the nearest neighbours and reconstruct our data point, then use
    # these weights with the existing embedding coordinates. I think if we use
    # the maximum dimension we would then get the 'total' variance ... or
    # that the we can just use the total variance of the original data points
    # (Then the LLE does 'nothing')

    explained_variances = np.zeros(d)
    explained_variances.fill(np.nan)

    d = min(d, X_train.shape[1])

    for i in range(d):
        lle = LocallyLinearEmbedding(n_components=i+1)
        lle.fit(X_train)
        explained_variances[i] = lle.transform(X_test).var(0).sum()

    # Find total variance
    # TODO confirm this works... Seems to give sensible results...
    lle = LocallyLinearEmbedding(n_components=X_train.shape[1])
    lle.fit(X_train)
    total_variance = lle.transform(X_test).var(0).sum()
    explained_variances /= total_variance

    return explained_variances


def run_ica(X_train, X_test, d):

    # TODO mostly works, sometimes it doesn't converge or takes ages to run...

    explained_variances = np.zeros(d)

    for i in range(d):
        print(i)
        ica = FastICA(n_components=i+1, tol=10e-3, max_iter=int(1e5))
        ica.fit(X_train)
        explained_variances[i] = ica.transform(X_test).var(0).sum()

    ica = FastICA(n_components=X_train.shape[1], tol=10e-3, max_iter=int(1e5))
    ica.fit(X_train)
    total_variance = ica.transform(X_test).var(0).sum()

    explained_variances /= total_variance

    return explained_variances



def run_isomap(X_train, X_test, d):

    # TODO determine best hyperparameter for n_neighbors

    explained_variances = np.zeros(d)

    isomap = Isomap(n_components=100, n_neighbors=10)
    isomap.fit(X_train)
    embedding_variances = isomap.transform(X_test).var(0)
    total_variance = embedding_variances.sum()
    explained_variances = np.cumsum(embedding_variances)[:d]

    return explained_variances


def run_nmf(X_train, X_test, d):

    explained_variances = np.zeros(d)

    for i in range(d):
        nmf = NMF(n_components=d+1, alpha=1)
        nmf.fit(X_train)
        explained_variances[i] = nmf.transform(X_test).var(0).sum()

    return explained_variances


def run_dictionary_learning(X_train, X_test, d):

    # Almost works (apart from normalization yet)

    explained_variances = np.zeros(d)

    for i in range(d):
        dic = DictionaryLearning(n_components=i+1)
        dic.fit(X_train)
        explained_variances[i] = dic.transform(X_test).var(0).sum()

    total_variance = np.sum(X_test.var(0)) # Sum of variances across all dimensions

    explained_variances /= total_variance

    return explained_variances


import argparse

description = "Comparison of unsupervised methods."
parser = argparse.ArgumentParser(description=description,
                                 parents=[base_parser])


if __name__ == '__main__':

    args = parser.parse_args()

    sys.exit(main(**vars(args)))

