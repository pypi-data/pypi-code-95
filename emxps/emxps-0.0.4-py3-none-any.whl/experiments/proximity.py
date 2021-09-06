import numpy as np
import scipy as sp

from ..xps import get_counter_methods_from_results
from tqdm import tqdm

from emutils.geometry.metrics import get_metric_name, get_metric_params


def compute_counterfactuals_proximity(
    xps_results,
    method,
    normalizer,
    metric='minkowski',
    normalize='std',
    **kwargs,
):
    # Pre-process metric
    metric = get_metric_name(metric)
    metric_params = get_metric_params(metric, **kwargs)

    def proximity(xps_results):
        for result in xps_results:
            x = normalizer.transform(np.array([result['x']]), method=normalize)
            X__ = normalizer.transform(result[method + '_X'], method=normalize)

            # L0 norm (i.e., number of non-zero)
            if 'l0_norm' == metric:
                yield ((X__ - np.tile(x, (len(X__), 1))) != 0).sum(axis=1)
            else:
                yield sp.spatial.distance.cdist(x, X__, metric=metric, **metric_params).flatten()

    return np.array(list(proximity(xps_results)))


def compute_all_proximity(xps_results, normalizer, metrics, loaded=None, **kwargs):
    if loaded is None:
        rets = None
    else:
        rets = loaded

    for method in get_counter_methods_from_results(xps_results):
        if method not in rets:
            rets[method] = {
                metric: compute_counterfactuals_proximity(
                    xps_results,
                    method=method,
                    normalizer=normalizer,
                    metric=metric,
                    normalize='std',
                    **kwargs,
                )
                for metric in tqdm(metrics, desc=method)
            }
    return rets