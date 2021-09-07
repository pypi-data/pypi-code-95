# %%
from collections import defaultdict
import numpy as np
import scipy as sp
import scipy.spatial

from emutils.utils import keydefaultdict
from emutils.parallel.batch import batch_process

NORM_NAMES = keydefaultdict(lambda l: f'L{l} Norm')

CUSTOM_DISTANCES = {
    'L0': 'hamming',
    'L1': 'cityblock',
    'L2': 'euclidean',

    # Alias
    'manhattan': 'cityblock',
    "cosine_distance": "cosine",

    # Minkowski np.inf
    'Linf': 'chebyshev',
    'max': 'chebyshev',

    # Weighted
    'wmanhattan': 'wcityblock',
    'wL1': 'wcityblock',
    'wL2': 'weuclidean',
}

CUSTOM_DISTANCES_SET = set(list(CUSTOM_DISTANCES))

PROXY_DISTANCES = {
    'wchebyshev': ('wminkowski', {
        'p': np.inf
    }),
    'weuclidean': ('wminkowski', {
        'p': 2
    }),
    'wcityblock': ('wminkowski', {
        'p': 1
    }),
}

RELATIVE_DISTANCE_NORM = defaultdict(
    lambda X, Y: np.ones(X.shape[0]), {
        'euclidean': lambda X, Y: np.linalg.norm((X + Y) / 2, ord=2, axis=1),
        'cityblock': lambda X, Y: np.linalg.norm((X + Y) / 2, ord=1, axis=1),
        'chebyshev': lambda X, Y: np.max((X + Y) / 2, axis=1),
    }
)


def adist(X, Y, metric, **metric_params):
    metric, metric_params = get_metric_name_and_params(metric, **metric_params)
    dist_func = getattr(sp.spatial.distance, metric)
    return np.array([dist_func(x, y, **metric_params) for x, y in zip(X, Y)])


def radist(X, Y, metric, **metric_params):
    dist = adist(X, Y, metric=metric, **metric_params)
    metric, metric_params = get_metric_name_and_params(metric, **metric_params)
    dist_n = RELATIVE_DISTANCE_NORM[metric](X, Y)
    return dist / dist_n


def norm_distance(x, y, **kwargs):
    return np.linalg.norm(x - y, **kwargs)


def get_metric_name(metric):
    if metric in CUSTOM_DISTANCES_SET:
        return CUSTOM_DISTANCES[metric]
    return metric


def get_metric_params(metric, **kwargs):
    metric_params = {}
    if metric == 'mahalanobis':
        if 'IV' in kwargs:
            metric_params.update({'VI': kwargs['IV']})
        # Use the data
        elif 'data' in kwargs:
            metric_params.update({'VI': sp.linalg.inv(np.cov(kwargs['data'], rowvar=False))})
        # Use the normalizer
        elif 'normalizer' in kwargs:
            method = kwargs['method'] if 'method' in kwargs else None
            lib = kwargs['lib'] if 'lib' in kwargs else 'np'
            metric_params.update({'VI': kwargs['normalizer'].covariance_matrix(data=None, method=method, lib=lib)})
    if metric == 'minkowski':
        metric_params.update(dict(p=kwargs['p']))

    if metric == 'wminkowski':
        metric_params.update(dict(w=kwargs['weight']))
    return metric_params


def get_metric_name_and_params(metric, **kwargs):
    metric = get_metric_name(metric)
    metric_params = get_metric_params(metric, **kwargs)
    return metric, metric_params


def cdist(
    X,
    Y,
    distance,
    aggregate=None,

    # Parallel
    split_size=None,
    desc=None,
    verbose=1,

    # Other metric params
    **kwargs,
):
    """
        Returns:
            X.shape[0] x Y.shape[0] if aggregate is None
            X.shape[0] otherwise
    """

    # Batching
    if split_size is not None:
        return batch_process(
            # Recursive call
            f=lambda X: pairwise_distance(
                X=X,
                Y=Y,
                distance=distance,
                aggregate=aggregate,
                split_size=None,
                **kwargs,
            ),
            iterable=X,
            split_size=split_size,
            desc=desc,
            n_jobs=1,  # It's not faster with more threads
            verbose=verbose,
        )

    # Get distance and params
    distance, metric_params = get_metric_name_and_params(distance, **kwargs)

    # Computation
    ret = sp.spatial.distance.cdist(
        X,
        Y,
        metric=distance,
        **metric_params,
    )

    # Aggregate distance
    if aggregate is not None:
        return aggregate(np.array(ret), axis=1)
    else:
        return np.array(ret)


pairwise_distance = cdist

# %%
