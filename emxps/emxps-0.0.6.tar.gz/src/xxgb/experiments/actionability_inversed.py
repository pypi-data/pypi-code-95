import logging
import warnings
import multiprocessing
import time
from collections import defaultdict
import itertools
import numpy as np
import scipy as sp
import statsmodels
import statsmodels.stats
import statsmodels.stats.proportion
import pandas as pd
import plotly.express as px

from tqdm import tqdm
from joblib import Parallel, delayed

from ..xps import get_methods_from_results
from ..monotonefeature import Feature, get_feature_objects
from ..xps.attribution.utils import xps_to_arrays

from .actionability import compute_max_ks, compute_confidence_intervals, join_results

# ███████╗██╗  ██╗███████╗ ██████╗██╗   ██╗████████╗██╗ ██████╗ ███╗   ██╗
# ██╔════╝╚██╗██╔╝██╔════╝██╔════╝██║   ██║╚══██╔══╝██║██╔═══██╗████╗  ██║
# █████╗   ╚███╔╝ █████╗  ██║     ██║   ██║   ██║   ██║██║   ██║██╔██╗ ██║
# ██╔══╝   ██╔██╗ ██╔══╝  ██║     ██║   ██║   ██║   ██║██║   ██║██║╚██╗██║
# ███████╗██╔╝ ██╗███████╗╚██████╗╚██████╔╝   ██║   ██║╚██████╔╝██║ ╚████║
# ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
#


class NormalizedFeature:
    def __init__(
        self,
        feature,
        normalizer,
        method,
    ):
        self.feature = feature

        # Inititialize normalized values and values together cache
        self.norm = {
            which: np.hstack(
                [
                    normalizer.feature_transform(
                        self.feature.values[which],
                        f=self.feature.idx,
                        method=method,
                    ).reshape(-1, 1),
                    self.feature.values[which].reshape(-1, 1),
                ]
            )
            for which in [-1, +1]
        }

    def get_norm_and_values_towards_change(self, x_i, target_class=0):
        if self.feature.is_useless():
            return np.array([]).reshape(-1, 2)

        assert target_class in [0, 1]

        # Which values  (left, right)
        which = -1 * (target_class - .5) * self.feature.trend
        vid = int(-1 + np.heaviside(which, .5) * 2)

        # Get values
        norm_values = self.norm[vid].copy()
        feature_values = norm_values[:, 1]

        if which < 0:
            iv = np.searchsorted(feature_values, x_i, side='right')
            norm_values = norm_values[iv:]
        elif which > 0:
            iv = np.searchsorted(feature_values, x_i, side='left')
            norm_values = norm_values[:iv]
        else:
            raise ValueError("Invalid value for which")

        return norm_values


def normalize_feature_objects(features_objs, normalizer, method):
    return [NormalizedFeature(
        feature=feat,
        normalizer=normalizer,
        method=method,
    ) for feat in features_objs]


def __get_cost_value_feature_tuples(fso, x, x_norm, pred, phi, also_negative_phi=False):
    """Returns the Cost & Values & Features that must be changed to change the prediction

    Args:
        fso (list): Subset of features objects
        x (np.ndarray): The current sample
        x_norm (np.ndarray): The current normalized sample
        pred (int): Current prediction

    Returns:
        np.ndarray: An array with size nb_values x 3
        Col 0 : Cost
        Col 1 : Value
        Col 3 : Feature (idx)
    """
    # Generate the Cost-Value-Feature Array
    cvfs = []
    for feat in fso:
        # The features are not ordered, we need to get the index again
        f = feat.feature.idx

        # We ignore features contributing 0
        if phi[f] == 0:
            continue

        # We only consider features that are contributing positively to the prediction
        if phi[f] < 0 and not also_negative_phi:
            continue

        # Get the Norm-Value array
        # nvs.shape[0] = nb_values
        # Col 0 : Normalized values
        # Col 1 : Values
        nvs = feat.get_norm_and_values_towards_change(
            x_i=x[f],
            target_class=1 - pred,
        )
        # Convert norm to cost-norm
        nvs[:, 0] = np.abs(nvs[:, 0] - x_norm[f])

        # Make it proportional
        nvs[:, 0] = nvs[:, 0] / np.abs(phi[f])

        # Append feature
        # Col 2 : Feature idx
        cvfs.append(np.hstack([
            nvs,
            np.ones(nvs.shape[0]).reshape(-1, 1) * f,
        ]))
    # Stack all together
    if len(cvfs) > 0:
        cvfs = np.vstack(cvfs)
    else:
        cvfs = np.array([]).reshape(0, 3)
    return cvfs


def __inf_costs_and_counter(x):
    return dict(L0=np.inf, L1=np.inf, L2=np.inf, Linf=np.inf), np.full(x.shape[0], np.nan),


def __find_costs_and_counterfactual(model, x, pred, cvfs):
    # cvf(s) = cost, value, feature (id)
    # do change until the prediction change and report the pec_shift
    X_prime = np.tile(x.copy(), (len(cvfs), 1))
    for i, (_, newval, f) in enumerate(cvfs):
        X_prime[i:, int(f)] = newval

    first_change = np.searchsorted((model.predict(X_prime) != pred) * 1, 1, side='left')

    # Get max cost per feature
    fcosts = np.zeros(len(x))
    for c, _, f in cvfs[:(first_change + 1)]:
        fcosts[int(f)] = max(fcosts[int(f)], c)

    # Return the maximum percentile shift and the total percentile shift
    if first_change < len(X_prime):
        # Column 0 contains costs
        # Return max cost (per feature), and total cost (sum of features), L2 norm (on the cost of the features)
        return dict(
            Linf=cvfs[first_change, 0],
            L1=fcosts.sum(),
            L2=np.linalg.norm(fcosts),
            L0=(fcosts > 0).sum(),
        ), X_prime[first_change]
    else:
        return __inf_costs_and_counter(x)


def __find_maxcost(model, x, pred, cvfs):
    # cvf(s) = cost, value, feature (id)
    # do change until the prediction change and report the pec_shift
    X_prime = np.tile(x.copy(), (len(cvfs), 1))
    for i, (_, newval, f) in enumerate(cvfs):
        X_prime[i:, int(f)] = newval

    first_change = np.searchsorted((model.predict(X_prime) != pred) * 1, 1, side='left')

    if first_change < len(X_prime):
        return cvfs[first_change, 0]
    else:
        return np.inf


def __find_counterfactual(
    x, maxcost, phi, features_mask, pred, feature_trends, normalizer, normalization_method, also_negative_phi=False
):
    __trends = np.array(feature_trends)
    __features_mask = np.zeros(len(x))
    __features_mask[features_mask] = 1  # Only top-k
    if not also_negative_phi:
        __features_mask = __features_mask * (phi > 0)  # Only if positive
    c = -1 * (pred * 2 - 1) * maxcost * __trends * __features_mask * np.abs(phi)
    return normalizer.move_transform(np.array([x]), costs=c, method=normalization_method)[0]


def __inverse_actionability_method(
    xps_results,
    method,
    normalizer,
    splits,
    feature_trends,
    model,
    normalization_method,
    ret_counter=False,
    mode='topk',
    # n_jobs=1,  #multiprocessing.cpu_count() - 1,
):
    """"
    
        mode : 
            'topk'        - Change top-k (from 1 to n) features with positive attribution of the same (normalized) amount and do this for all k
            'topn'        - Change all features with positive attribution of a (normalized) amount proportional to their attribution
            '...-vector'  - Will change the features of a (normalized) amount proportional to their attribution
            '...-both'    - Will change also the features that are not positive
    """
    # Arguments proprecessing
    if 'topk' in mode:
        Ks = range(1, len(splits) + 1)
    elif 'topn' in mode:
        Ks = [len(splits)]
    elif mode.startswith('top'):
        Ks = [int(mode.split('-')[0][3:])]
        assert Ks[0] <= len(splits), 'Top-K greater than the number of features'
    else:
        raise ValueError('Invalid mode.')

    if 'vector' in mode:
        phi_proportional = True
    else:
        phi_proportional = False

    if 'both' in mode:
        also_negative_phi = True
    else:
        also_negative_phi = False

    # Create features objects
    features_objs = np.array(
        normalize_feature_objects(
            features_objs=get_feature_objects(splits, None, feature_trends=feature_trends),
            normalizer=normalizer,
            method=normalization_method,
        )
    )

    # Compute stuff from the results
    xps_arrays = xps_to_arrays(xps_results, only_methods=False, only_methods_and_X=False)
    X_ = xps_arrays['x']
    X_norm_ = normalizer.transform(X_, method=normalization_method)
    Phi = xps_arrays[method]
    Pred = xps_arrays['pred']

    if also_negative_phi:
        Order = np.argsort(-1 * np.abs(Phi), axis=1)
    else:
        Order = np.argsort(-1 * Phi, axis=1)

    if not np.all(Pred == 1):
        warnings.warn('Class is not 1!')

    # Iterate
    results = []  # Samples x Dict(Cost : Top-K)
    results_counter = []  # Samples x Top-K x nb_features

    def do_fa_recourse(x, x_norm, phi, pred, feat_order):
        topk_costs = []
        topk_counter = []
        # Iterate over the Ks
        for k in Ks:
            if np.any(np.isnan(phi)):
                warnings.warn(f'NaN feature attribution (method = {method})')
                # If the feature attribution is NaN we return infinite and nan
                costs, x_counter = __inf_costs_and_counter(x)
            else:
                phix = phi if phi_proportional else 1 * (phi > 0) + (phi < 0) * -1
                # Take the k most important features
                fso = features_objs[feat_order[:k]]
                # Compute all the subsequent changes that can be done to change the prediction
                cvfs = __get_cost_value_feature_tuples(
                    fso=fso,
                    x=x,
                    x_norm=x_norm,
                    pred=pred,
                    phi=phix,
                    also_negative_phi=also_negative_phi,
                )
                if len(cvfs) == 0 and (phix > 0).sum() > 0:
                    warnings.warn('len(cvfs) is 0 but phi is positive!')
                # Sort the iterator by cost
                # cvfs n x 3
                # Column 0 : Cost
                # Column 1 : Value to which to change to pay such cost
                # Column 2 : Feature to change
                cvfs = cvfs[cvfs[:, 0].argsort()]

                # Compute cost
                costs, x_counter = __find_costs_and_counterfactual(
                    model=model,
                    x=x,
                    pred=pred,
                    cvfs=cvfs,
                )

                # maxcost = __find_maxcost(
                #     model=model,
                #     x=x,
                #     pred=pred,
                #     cvfs=cvfs,
                # )
                maxcost = costs['Linf']
                if not np.isinf(maxcost):
                    x_counter = __find_counterfactual(
                        x=x,
                        phi=phix,
                        pred=pred,
                        features_mask=feat_order[:k],
                        maxcost=costs['Linf'],
                        normalizer=normalizer,
                        normalization_method=normalization_method,
                        feature_trends=feature_trends,
                        also_negative_phi=also_negative_phi,
                    )

            # Append results
            topk_costs.append(costs)
            topk_counter.append(x_counter)
        return topk_costs, topk_counter

    # Compute stuff in parallel (list of tuples (topk_costs, topk_counter))
    # if n_jobs > 1:
    #     par_results = Parallel(n_jobs=n_jobs)(
    #         delayed(do_fa_recourse)(x, x_norm, phi, pred, feat_order)
    #         for x, x_norm, phi, pred, feat_order in tqdm(zip(X_, X_norm_, Phi, Pred, Order), desc=method)
    #     )
    # else:
    par_results = [
        do_fa_recourse(x, x_norm, phi, pred, feat_order)
        for x, x_norm, phi, pred, feat_order in tqdm(zip(X_, X_norm_, Phi, Pred, Order), desc=method)
    ]

    # Extract results
    results = [pd.DataFrame(x[0]).to_dict('list') for x in par_results]
    results_counter = np.array([x[1] for x in par_results])

    if ret_counter:
        return results, np.array(results_counter)
    else:
        return results


def all_inverse_actionability(xps_results, *args, methods=None, loaded=None, ret_counter=False, **kwargs):
    if methods is not None:
        methods = set(get_methods_from_results(xps_results)) & set(methods)
    else:
        methods = get_methods_from_results(xps_results)
    if loaded is None:
        rets, counters = {}, {}
    else:
        if isinstance(loaded, tuple):
            rets, counters = loaded
        else:
            rets, counters = loaded, {}

    for method in methods:
        if method not in rets or (ret_counter and method not in counters):
            ret = __inverse_actionability_method(
                xps_results,
                *args,
                method=method,
                ret_counter=ret_counter,
                **kwargs,
            )
            if ret_counter:
                rets[method], counters[method] = ret
            else:
                rets[method] = ret
    if ret_counter:
        return rets, counters
    else:
        return rets


# ██████╗  █████╗ ████████╗ █████╗     ████████╗██████╗  █████╗ ███████╗███████╗ ██████╗ ██████╗ ███╗   ███╗
# ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝██╔═══██╗██╔══██╗████╗ ████║
# ██║  ██║███████║   ██║   ███████║       ██║   ██████╔╝███████║███████╗█████╗  ██║   ██║██████╔╝██╔████╔██║
# ██║  ██║██╔══██║   ██║   ██╔══██║       ██║   ██╔══██╗██╔══██║╚════██║██╔══╝  ██║   ██║██╔══██╗██║╚██╔╝██║
# ██████╔╝██║  ██║   ██║   ██║  ██║       ██║   ██║  ██║██║  ██║███████║██║     ╚██████╔╝██║  ██║██║ ╚═╝ ██║
# ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝
# %%
def swapaxes_and_select(reaction_results, what, methods=None):
    selected_results = defaultdict(list)
    for effects_results in reaction_results:
        for method, results in effects_results.items():
            if (methods is not None) and (method not in methods):
                continue
            selected_results[method].append(np.array([r[what] for r in results]))
    for method, results in selected_results.items():
        selected_results[method] = np.array(results)
    return selected_results


def join_and_select_farclose(reac_close, reac_far, what):
    ret = {}
    for method in reac_close.keys():
        lenght = len(reac_close[method][0]['Linf'])

        # Some trailing np.inf are missing in some experiments, we fix those padding to the number of features
        def pad_with_inf(a):
            return np.pad(
                np.array(a),
                mode='constant',
                pad_width=(lenght - len(a), 0),
                constant_values=np.inf,
            )

        ret.update(
            {
                method + '_c': np.array([pad_with_inf(r[what]) for r in reac_close[method]]),
                method + '_f': np.array([pad_with_inf(r[what]) for r in reac_far[method]]),
            }
        )
    return ret


# ███████╗████████╗ █████╗ ████████╗███████╗
# ██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██╔════╝
# ███████╗   ██║   ███████║   ██║   ███████╗
# ╚════██║   ██║   ██╔══██║   ██║   ╚════██║
# ███████║   ██║   ██║  ██║   ██║   ███████║
# ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚══════╝
# %%


def compute_confidence_intervals_proportion(aggr_res, apply=lambda x: x):
    lower = defaultdict(list)
    upper = defaultdict(list)
    for method, values in aggr_res.items():
        counts = apply(values)
        for v in counts:
            l, u = statsmodels.stats.proportion.proportion_confint(
                count=max(0, min(len(values), v * len(values))),
                nobs=len(values),
                alpha=.05,
                method='beta',
            )
            lower[method].append(v - l)
            upper[method].append(u - v)

    lower = {method: np.array(a) for method, a in lower.items()}
    upper = {method: np.array(a) for method, a in upper.items()}
    return lower, upper


# ██████╗ ██╗      ██████╗ ████████╗██╗  ██╗   ██╗
# ██╔══██╗██║     ██╔═══██╗╚══██╔══╝██║  ╚██╗ ██╔╝
# ██████╔╝██║     ██║   ██║   ██║   ██║   ╚████╔╝
# ██╔═══╝ ██║     ██║   ██║   ██║   ██║    ╚██╔╝
# ██║     ███████╗╚██████╔╝   ██║   ███████╗██║
# ╚═╝     ╚══════╝ ╚═════╝    ╚═╝   ╚══════╝╚═╝
# %%


def plotly_infinite(
    df,
    max_ks=None,
    lower=None,
    upper=None,
    value_name="Rate",
):
    """
        df:
            # Columns = Methods
            # Rows = Top-features changed
            # Values = Rate of infinite
    """

    var_name = 'XP'
    top_col_name = 'top'

    # Add KS to the method name
    if max_ks is not None:
        df.rename(
            columns={method: method + f" (KS={str(np.round(max_ks[method], 4))[:6]})"
                     for method in df.columns.values},
            inplace=True
        )

    # Filter high top-k for which there is no infinite rate (=0.0)
    max_f = np.searchsorted(1 * ((df.values != 0).sum(axis=1) == 0), 1, side='left')
    df = df.iloc[:max_f]
    df[top_col_name] = np.arange(len(df)) + 1

    # Melt
    df = df.melt(
        id_vars=[top_col_name],
        var_name=var_name,
        value_name=value_name,
    )

    # Add confidence intervals
    if lower is not None:
        df['lower'] = pd.DataFrame(lower).iloc[:max_f].melt()['value'].values
    if upper is not None:
        df['upper'] = pd.DataFrame(upper).iloc[:max_f].melt()['value'].values

    # Plot
    fig = px.line(
        df,
        x=top_col_name,
        y=value_name,
        color=var_name,
        title="Failure rate in changing the prediction by using the top-k features",
        error_y='upper' if upper is not None else None,
        error_y_minus='lower' if lower is not None else None,
    )
    fig.update_traces(
        hoverinfo='text+name',
        mode='lines+markers',
    )
    fig.update_layout(
        yaxis_tickformat='.2%',
        xaxis_title='Number of top features changed (k)',
    )
    fig.show()


from emutils.geometry.normalizer import get_normalization_name


def get_value_name(distance, what):

    if distance is not None:
        norm_name = get_normalization_name(distance)
    else:
        norm_name = ''

    WHAT_DICT = {
        'Linf': 'Maximum',
        'L1': 'Total',
        'L2': 'L2 Norm of',
        'L0': 'Number of different features',
    }

    if what is not None:
        what_name = WHAT_DICT[what]
    else:
        what_name = ''

    return f"{what_name} {norm_name}".strip()


def get_how_name(mode):
    if 'vector' in mode:
        return 'changing top-k features proportionally'
    else:
        return 'changing top-k feature together'


def plotly_rev_actionability(
    means,
    max_ks=None,
    upper=None,
    lower=None,
    top=None,
    fig=None,
    value_name="Maximum Percentile Shift",
    how_name="",
):
    var_name = "XP"

    # Transform to dataframe
    df = pd.DataFrame(means)

    # Add KS to the method name
    if max_ks is not None:
        df.rename(
            columns={
                method: method + f" (KS={str(np.round(max_ks[method], 4))[:6]})"
                for method in df.columns.values if max_ks is not None
            },
            inplace=True
        )

    # Filter only top-k
    df['top'] = df.index.values + 1
    if top is not None:
        df = df.iloc[:top]

    # Melt
    df = df.melt(id_vars=['top'], var_name=var_name, value_name=value_name)
    if upper is not None and lower is not None:
        df['lower'] = pd.DataFrame(lower).melt()['value'].values
        df['upper'] = pd.DataFrame(upper).melt()['value'].values

    # Plot
    fig = px.line(
        df,
        y=value_name,
        color=var_name,
        x='top',
        error_y='upper' if upper is not None else None,
        error_y_minus='lower' if lower is not None else None,
    )
    fig.update_traces(
        hoverinfo='text+name',
        mode='lines+markers',
    )
    fig.update_layout(
        title=f"""Cost (in terms of {value_name.lower()}) to change<br>the prediction {how_name}
        """,
        xaxis_title='Number of top features changed (k)',
    )
    fig.update_layout(yaxis_tickformat='.2%')
    fig.show()


# ███╗   ███╗ █████╗ ██╗███╗   ██╗    ██╗  ██╗ █████╗ ███╗   ██╗██████╗ ██╗     ███████╗███████╗
# ████╗ ████║██╔══██╗██║████╗  ██║    ██║  ██║██╔══██╗████╗  ██║██╔══██╗██║     ██╔════╝██╔════╝
# ██╔████╔██║███████║██║██╔██╗ ██║    ███████║███████║██╔██╗ ██║██║  ██║██║     █████╗  ███████╗
# ██║╚██╔╝██║██╔══██║██║██║╚██╗██║    ██╔══██║██╔══██║██║╚██╗██║██║  ██║██║     ██╔══╝  ╚════██║
# ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║    ██║  ██║██║  ██║██║ ╚████║██████╔╝███████╗███████╗███████║
# ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝╚══════╝
#


def plot_infinite_rate(reaction_results, methods=None, distance=None):

    # Results non-aggregated
    # dict of list of Numpy (one list element per sample of ~1000)
    nonaggr_res = swapaxes_and_select(
        reaction_results,
        what='Linf',
        methods=methods,
    )
    # Results aggregated
    # dict of Numpy
    aggr_res = join_results(nonaggr_res)

    # Function to compute the rate of np.inf
    def __count_infinite(values):
        return np.isinf(values).sum(axis=0) / len(values)

    # Compute rates (aggregated for all samples)
    infinite_rate = {method: __count_infinite(values) for method, values in aggr_res.items()}

    # Compute Max KS Divergence between samples
    max_ks = compute_max_ks(nonaggr_res, apply=__count_infinite)

    # Computer confidence intervals
    lower, upper = compute_confidence_intervals_proportion(aggr_res, apply=__count_infinite)

    # Cols: methods / Rows: nb_top_features / Values: rate
    infinite_rate = pd.DataFrame(infinite_rate)

    # Plot
    plotly_infinite(
        infinite_rate,
        max_ks=max_ks,
        lower=lower,
        upper=upper,
        # value_name=get_value_name(distance, None),
    )


def plot_rev_actionability(reaction_results, what, methods=None, safe=True, distance=None, mode=None):
    """
        what : result to plot

        i.e. 'Linf' or 'L1'
    """
    # Select results
    # dict (of methods) of list (of samples) of NumPy (nb_samples x nb_features)
    nonaggr_res = swapaxes_and_select(
        reaction_results,
        what=what,
        methods=methods,
    )

    # Aggregate results
    # dict (of methods) of NumPy (tot_nb_samples x nb_features)
    aggr_res = join_results(nonaggr_res)

    # Function to be applied
    def __safe_mean(x):
        # Transform np.inf into 1.0 (100%)
        if safe:
            return np.mean(np.nan_to_num(x, posinf=1), axis=0)
        else:
            return np.mean(x, axis=0)

    # Compute means
    means = {method: __safe_mean(results) for method, results in aggr_res.items()}

    # Compute KS divergence
    max_ks = compute_max_ks(nonaggr_res, apply=__safe_mean)

    # Computer confidence intervals
    lower, upper = compute_confidence_intervals(
        aggr_res,
        apply=lambda x: np.nan_to_num(x, posinf=1),
    )

    # Plot it
    plotly_rev_actionability(
        means=means,
        max_ks=max_ks,
        lower=lower,
        upper=upper,
        value_name=get_value_name(distance, what),
        how_name=get_how_name(mode),
    )


def plot_aar_close_far_infinite(reac_close, reac_far, distance, what='Linf'):

    # Results
    # dict of ([method_close, method_far, method2_close, ...]) NumPy (tot_nb_samples x nb_features)
    aggr_res = join_and_select_farclose(reac_close=reac_close, reac_far=reac_far, what=what)

    print(f"Using {len(aggr_res[list(aggr_res.keys())[0]])} samples.")

    # Function to compute the rate of np.inf
    def __count_infinite(values):
        return np.isinf(values).sum(axis=0) / len(values)

    # Compute rates (aggregated for all samples)
    infinite_rate = {method: __count_infinite(values) for method, values in aggr_res.items()}

    # Computer confidence intervals
    lower, upper = compute_confidence_intervals_proportion(aggr_res, apply=__count_infinite)

    # Cols: methods / Rows: nb_top_features / Values: rate
    infinite_rate = pd.DataFrame(infinite_rate)

    # Plot
    plotly_infinite(
        infinite_rate,
        max_ks=None,
        lower=lower,
        upper=upper,
        value_name=get_value_name(distance, None),
    )


def plot_aar_close_far(reac_close, reac_far, what, distance, safe=True):
    """
        what : result to plot

        i.e. 'Linf' or 'L1'
    """

    # Results
    # dict of ([method_close, method_far, method2_close, ...]) NumPy (tot_nb_samples x nb_features)
    aggr_res = join_and_select_farclose(reac_close=reac_close, reac_far=reac_far, what=what)

    print(f"Using {len(aggr_res[list(aggr_res.keys())[0]])} samples.")

    # Function to be applied
    def __safe_mean(x):
        # Transform np.inf into 1.0 (100%)
        if safe:
            return np.mean(np.nan_to_num(x, posinf=1), axis=0)
        else:
            return np.mean(x, axis=0)

    # Compute means
    means = {method: __safe_mean(results) for method, results in aggr_res.items()}

    # Computer confidence intervals
    lower, upper = compute_confidence_intervals(
        aggr_res,
        apply=lambda x: np.nan_to_num(x, posinf=1),
    )

    # Plot it
    plotly_rev_actionability(
        means=means,
        max_ks=None,
        lower=lower,
        upper=upper,
        value_name=get_value_name(distance, what),
    )
