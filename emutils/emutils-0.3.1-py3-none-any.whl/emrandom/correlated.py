import numpy as np
import scipy as sp
import scipy.stats

__all__ = [
    'covariance_matrix_from_correlation',
    'generate_binary_label',
    'generate_random_correlated_data',
]


def covariance_matrix_from_correlation(rho):
    return np.array([
        [1, rho],
        [rho, 1],
    ])


def generate_random_correlated_data(
    Kxx=[
        [1, .9],
        [.9, 1],
    ],
    n=1000,
    dim=2,
    method='cholesky',
    random_state=None,
    stat='norm',
    **kwargs,
):
    # Generate samples from three independent normally distributed random
    # variables (with mean 0 and std. dev. 1).
    if isinstance(stat, str):
        dist = getattr(sp.stats, stat)
        if random_state is not None:
            dist.random_state = np.random.RandomState(random_state)

        X = dist.rvs(size=(dim, n), **kwargs)

    else:
        X = np.vstack([getattr(sp.stats, s).rvs(size=(1, n), **kwargs) for s in stat])

    print(X.shape)
    # We need a matrix `c` for which `c*c^T = r`.  We can use, for example,
    # the Cholesky decomposition, or the we can construct `c` from the
    # eigenvectors and eigenvalues.

    if method == 'cholesky':
        # Compute the Cholesky decomposition.
        C = sp.linalg.cholesky(Kxx, lower=True)
    elif method == 'eigen':
        # Compute the eigenvalues and eigenvectors.
        evals, evecs = sp.linalg.eigh(Kxx)
        # Construct c, so c*c^T = r.
        C = np.dot(evecs, np.diag(np.sqrt(evals)))
    else:
        raise ValueError('Invalid method.')

    # Convert the data to correlated random variables.
    return np.dot(C, X).T


def generate_binary_label(X, func, fraction, ret_threshold=False):
    y = func(X)
    y_threshold = np.sort(y)[int(min(len(y), max(0, round(len(y) * fraction))))]
    y = 1 * (y >= y_threshold)
    y = y.astype(int)
    if ret_threshold:
        return y, y_threshold
    else:
        return y