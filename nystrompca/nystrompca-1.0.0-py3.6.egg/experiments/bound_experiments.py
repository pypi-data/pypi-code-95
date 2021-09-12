
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
Experiments to evaluate Nyström kernel PCA and the confidence bound,
comparing it to standard kernel PCA and kernel PCA using the subset
of data points directly.

"""

# Built-in modules
import sys
import time
from multiprocessing import Pool, cpu_count

# Third-party packages
import numpy as np
import pandas as pd
from sklearn.preprocessing import scale

# This package
from nystrompca import NystromKPCA, calculate_bound
from nystrompca.experiments import base_parser, data, plot_results
from nystrompca.base import Kernel
from nystrompca.utils import logger, get_eigendecomposition, get_tail_sums


# Always display numbers in decimal format, using 4 decimals
pd.options.display.float_format = '{:,.4f}'.format


def main(kernel:  str = "",
         n:       int = 1000,
         m:       int = 20,
         d:       int = 10,
         samples: int = 1,
         save:   bool = False) -> int:
    """
    Run the experiments four different datasets.

    After each plot is shown the program halts, close the plot to continue.

    Parameters
    ----------
    kernel: str
        Kernel function to use
    n : int
        Total size of dataset
    m : int
        Size of subsampled dataset
    d : int
        Maximum PCA dimension
    samples : int
        Number of subset samples to average
    save : bool
        Whether to store the figures on disk

    Returns
    -------
    int
        Return code, 0 if success

    """
    logger.header("Nyström kernel PCA Experiments")

    logger.info("Kernel: {}".format(kernel))
    logger.info("n: {}".format(n))
    logger.info("m: {}".format(m))
    logger.info("samples: {}".format(samples))

    all_results = pd.DataFrame()

    for dataset in ('magic', 'yeast', 'cardiotocography', 'segmentation'):

        logger.subheader("Dataset: {}".format(dataset))

        X = getattr(data, "get_" + dataset + "_data")(n)

        results = run_one_experiment(kernel, X, m, d, samples)
        logger.info("Results:")
        logger.info(results)
        #logger.info(results[['d',
        #                     'Nyström diff.',
        #                     'Subset diff.',
        #                     'Conf. bound',
        #                     'Total variance']])

        results['dataset'] = dataset

        all_results = all_results.append(results)

    all_results.reset_index(drop=True, inplace=True)

    plot_results(all_results, kernel, save=save)

    return 0


def run_one_experiment(kernel:  str,
                       X:       np.ndarray,
                       m:       int,
                       d:       int,
                       samples: int       ) -> pd.DataFrame:
    """
    Run an experiment for one kernel and dataset.

    Calculate the Nyström PCA bound, the actual difference between the
    Nyström and full reconstruction errors, and the difference between
    the full reconstruction error and the reconstruction error for the
    PCA subspace from the subset directly, for a number of different
    PCA subspace dimensions.

    The functions calculates the Nyström errors and bounds for multiple
    different subset samples and then takes the average. This is done
    in parallel using the maximum number of available CPU cores.

    Parameters
    ----------
    kernel : str
        Kernel function
    X : numpy.ndarray, 2d
        Data matrix, with observations in the rows
    m : int
        The size of the Nyström subset
    d : int
        Maximum PCA dimension
    samples : int
        Number of samples over which to calculate the Nyström quantities

    Returns
    -------
    results : pandas.DataFrame
        The results of one experiment

    """
    n = X.shape[0]

    if samples == 1:
        results = get_nystrom_results(X, kernel, d, m)

    else:
        with Pool(cpu_count()) as p:
            results = p.starmap(get_nystrom_results, samples*[(X, kernel, d, m)])

        results = pd.concat(results, axis=0)

        results = results.groupby('d', as_index=False).mean()

    t_elapsed = results['t_elapsed'].iloc[0]
    logger.info("Nyström KPCA elapsed time: {:.3f}".format(t_elapsed))

    true_errors, total_variance, t_elapsed = get_true_errors(X, kernel, d)

    logger.info("Kernel PCA elapsed time: {:.3f}".format(t_elapsed))

    results['True errors']    = true_errors
    results['Nyström diff.']  = results['Nyström errors'] - true_errors
    results['Subset diff.']   = results['Subset errors']  - true_errors
    results['Total variance'] = total_variance

    # TODO the 'Nystrom diff' and 'Subset diff' are very tiny ... also for other datasets
    # Check that it's correct and if I can make it larger somehow...

    # Some values may be zero within machine epsilon, set these to exactly zero
    results[np.abs(results) < 1e-14] = 0

    return results


def get_nystrom_results(X:      np.ndarray,
                        kernel: str,
                        d:      int,
                        m:      int       ) -> pd.DataFrame:
    """
    Get experimental results for one Nyström PCA experiment, for one
    sampling of the subset.

    Calculates the reconstruction errors, explained variances,
    subset PCA reconstruction errors and the confidence bounds
    for multiple PCA dimensions. Also calculate the process time
    taken to calculate the Nyström PCA solution.

    Parameters
    ----------
    X : numpy.ndarray, 2d
        Data matrix
    kernel : str
        Name of kernel function, supplied to the NystromKPCA class.
    d : int
        Maximum PCA dimension
    m : int
        Subset size

    Returns
    -------
    one_result : pandas.DataFrame
        Table with results, with columns 'd', 'Nyström errors', 'Nyström PCA',
        'Subset errors', 'Conf. bound', 't_elapsed', and with each row
        containing the results for one PCA dimension

    """
    n = X.shape[0]

    nystrom_kpca = NystromKPCA(kernel       = kernel,
                               n_components = d,
                               m_subset     = m,
                               demean       = False)

    t0 = time.process_time()
    nystrom_kpca.fit_transform(X)
    t_elapsed = time.process_time() - t0

    one_result = pd.DataFrame()

    # TODO the nystrom and subset errors are too small... They were larger before!
    # Fix.
    one_result['d']              = np.arange(d) + 1
    one_result['Nyström errors'] = nystrom_kpca.get_reconstruction_errors()
    one_result['Nyström PCA']    = get_tail_sums(nystrom_kpca.all_variances)[:d]

    one_result['Subset errors']  = nystrom_kpca.get_subset_errors()

    one_result['Conf. bound']    = calculate_bound(nystrom_kpca.K_mm_p, n,
                                                   nystrom_kpca.kernel.get_bound()
                                                   )[:d]

    print()
    print("K_mm")
    print(nystrom_kpca.K_mm_p)
    print()
    one_result['t_elapsed'] = t_elapsed

    return one_result


def get_true_errors(X:      np.ndarray,
                    kernel: str,
                    d:      int       ) -> (np.ndarray, float, float):
    """
    Calculate the reconstruction error for standard kernel PCA

    Parameters
    ----------
    X : numpy.ndarray, 2d
        Data matrix
    kernel : str
        Name of kernel function, supplied to the NystromKPCA class.
    d : int
        Maximum PCA dimension

    Returns
    -------
    true_errors : numpy.ndarray
        Standard kernel PCA reconstruction errors for all PCA dimensions
    total_variance : float
        The total "variance" of the data (reconstruction error for
        an empty subspace)
    t_elapsed : float
        Process time for calculating the standard kernel PCA solution

    """
    n = X.shape[0]

    kernel = Kernel(kernel)

    t0 = time.process_time()
    K = kernel.matrix(scale(X), demean=False)
    L, _ = get_eigendecomposition(K / X.shape[0])
    t_elapsed = time.process_time() - t0 # TODO do the time check in the methods comparison experiment instead!

    # Reconstruction errors for PCA on the entire dataset (for all d)
    true_errors = get_tail_sums(L, d)

    # Maximum reconstruction error
    total_variance = np.trace(K) / n

    return true_errors, total_variance, t_elapsed


import argparse

description = "Run experiments for Nyström kernel PCA and the confidence bound."
parser = argparse.ArgumentParser(description=description,
                                 parents=[base_parser])

parser.add_argument('--samples', default=1, type=int,
                    help="number of subset samples to average")


if __name__ == '__main__':

    args = parser.parse_args()

    sys.exit(main(**vars(args)))

