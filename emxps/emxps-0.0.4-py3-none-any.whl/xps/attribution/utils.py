import time
import logging
from copy import deepcopy
from xxgb.xps.attribution.cf import CFExplainer

import numpy as np
import pandas as pd

from emutils.utils import import_tqdm
from emutils.utils import random_stability

from emutils.geometry.ball import generate_random_point_inside_balls

tqdm = import_tqdm()


def xps_to_arrays(xps, only_methods=True, only_methods_and_X=True):
    # Get methods
    methods_ = get_methods_from_results(xps)

    # Transform all or only methods
    if only_methods:
        keys = methods_
    elif only_methods_and_X:
        keys = list(methods_) + ['x']
    else:
        keys = list(xps[0].keys())

    nb_features = len(xps[0]['x'])

    def __safe_none(phi):
        return np.full(nb_features, np.nan) if phi is None else phi

    def __warning_none(phi):
        if phi is None:
            logging.warning('Some elements are none')
        return phi

    return {
        k: np.array([deepcopy(__safe_none(r[k])) if k in methods_ else __warning_none(r[k]) for r in xps])
        for k in keys
    }


def is_xp_col(col):
    if not isinstance(col, str):
        return True
    if col in ['pred', 'prob', 'x', 'x_prime', 'epsilon', 'eps', 'x_nonrecoded']:
        return False
    if any([col.endswith(c) for c in ['_X', '_tweaks', '_X_len', '_Xaggr']]):
        return False
    return True


def filter_only_explanations(xps):
    def __filter(r):
        return {k: v for k, v in r.items() if is_xp_col(k)}

    if isinstance(xps, dict):
        return __filter(xps)
    return [__filter(r) for r in xps]


def __methods(result):
    return [key for key in result.keys() if is_xp_col(key)]


def get_methods_from_results(xp_results):
    if isinstance(xp_results, dict):
        return __methods(xp_results)
    else:
        return __methods(xp_results[0])


def get_counter_methods_from_results(xp_results):
    return [method for method in get_methods_from_results(xp_results) if method.startswith('counter')]


def compute_xps(
    x, model, explainers, res=None, res_add=None, debug=False, profile=False, soft_debug=True, transform_tweaks=True
):
    # New computation
    if res is None:
        res = dict(
            prob=model.predict_proba(x.reshape(1, -1))[:, 1],
            pred=model.predict(x.reshape(1, -1)),
            x=x.copy(),
        )
    # Resume computation
    else:
        x = res['x']

    # Add additional fields
    if res_add is not None:
        for k, v in res_add.items():
            if k not in res:
                res[k] = v

    # Compute new explanations
    for name, explainer in explainers.items():
        if profile:
            start = time.time()

        if name not in res:
            # Compute attributions
            X_ = x.reshape(1, -1)
            sres = explainer.shap_values(X_)
            res[name] = sres[0] if sres is not None else None

            # Add debug information
            if debug:
                if 'last_X' in dir(explainer):
                    res[name + "_X"] = explainer.last_X
                if 'last_tweaks' in dir(explainer):
                    res[name + "_tweaks"] = [t.debug_dict() for t in explainer.last_tweaks]

        if profile:
            print(f"{name} took {time.time() - start} seconds to generate a single explanation.")

    # Resume on all existing explanations
    for name in get_methods_from_results(res):
        name = str(name)
        # Add more debug information
        if soft_debug:
            if (name + "_X_len" not in res) and (name + "_X" in res):
                res[name + "_X_len"] = len(res[name + "_X"]) if res[name + "_X"] is not None else 0

        # Transform tweaks into dicts
        if transform_tweaks:
            if name + "_tweaks" in res and not isinstance(res[name + "_tweaks"][0], dict):
                res[name + "_tweaks"] = [t.debug_dict() for t in res[name + "_tweaks"]]

    return res


def filter_empty_explanations(xps_results):
    ret = [result for result in xps_results if not np.any([r is None for r in result.values()])]
    logging.info(
        'Filtered {nb_filtered} samples out of {tot}. There are {remain} remaining.',
        nb_filtered=len(xps_results) - len(ret),
        tot=len(xps_results),
        remain=len(ret),
    )
    return ret


def arrays_to_list(xps_arrays):
    return [
        {k: deepcopy(v[i])
         for k, v in xps_arrays.items() if isinstance(v, (list, np.ndarray))} for i in range(len(xps_arrays['x']))
    ]


def compute_xps_batch(X, *args, xps_results=None, X_nonrecoded=None, desc='Samples', **kwargs):
    # Index from which the samples are new
    if xps_results is None:
        start_index = 0
    else:
        start_index = len(xps_results)

    resx = []
    # Resume the computation computed samples
    if start_index > 0:
        resx.extend(
            [
                compute_xps(
                    None,
                    *args,
                    res=res,
                    res_add={'x_nonrecoded': X_nonrecoded[r]} if X_nonrecoded is not None else None,
                    **kwargs,
                ) for r, res in enumerate(tqdm(xps_results, desc=f'{desc}: Resumed'))
            ]
        )
    # Compute the explanations for new samples
    if start_index < len(X):
        resx.extend(
            [
                compute_xps(
                    x,
                    *args,
                    res_add={'x_nonrecoded': X_nonrecoded[start_index + r]} if X_nonrecoded is not None else None,
                    **kwargs,
                ) for r, x in enumerate(tqdm(X[start_index:], desc=f'{desc}: from {start_index}'))
            ]
        )

    # Return all
    return resx


# Compute SHAP for a sample of samples
def compute_xps_epsilon_batch(xps_results, normalizer, mode, phi, random_state, **kwargs):
    # Stabilize
    random_stability(random_state)

    # Generate epsilon deviated points
    X_ = np.array([r['x'] for r in xps_results])
    X_prime = generate_random_point_inside_balls(
        X_,
        normalizer=normalizer,
        mode=mode,
        phi=phi,
    )

    assert len(X_) == len(X_prime)

    return compute_xps_batch(X_prime, **kwargs)


# %%


def xps_to_df(xp_result, features_info=None, sort=True):
    df = pd.DataFrame({k: v for k, v in xp_result.items() if is_xp_col(k)})
    for col in df:
        df[col + "_rank"] = (-1 * df[col]).rank()
    if 'x' in xp_result:
        df['x'] = xp_result['x']
    if sort:
        df = df.reindex(sorted(df.columns), axis=1)
    if features_info is not None:
        df = pd.concat([df, features_info], axis=1)
    return df
