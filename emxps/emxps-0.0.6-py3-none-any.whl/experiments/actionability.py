import logging
from collections import defaultdict
import itertools
import time

import scipy as sp
import scipy.stats as stats
import numpy as np
import pandas as pd
import plotly.express as px

from tqdm import tqdm

from ..xps import get_methods_from_results

# ███████╗██╗  ██╗███████╗ ██████╗██╗   ██╗████████╗██╗ ██████╗ ███╗   ██╗
# ██╔════╝╚██╗██╔╝██╔════╝██╔════╝██║   ██║╚══██╔══╝██║██╔═══██╗████╗  ██║
# █████╗   ╚███╔╝ █████╗  ██║     ██║   ██║   ██║   ██║██║   ██║██╔██╗ ██║
# ██╔══╝   ██╔██╗ ██╔══╝  ██║     ██║   ██║   ██║   ██║██║   ██║██║╚██╗██║
# ███████╗██╔╝ ██╗███████╗╚██████╗╚██████╔╝   ██║   ██║╚██████╔╝██║ ╚████║
# ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
#


def __counterfactual_effets(
    x,
    prob,
    pred,
    vals,
    x_prime,
    keep_previous_changes,
    model,
):
    # Create modified samples
    X_prime = np.tile(x, (len(x), 1))

    feat_order = np.argsort(-1 * vals)
    for i, f in enumerate(feat_order):  # Rank features from the most important (positive SHAP)
        # Do the change
        if keep_previous_changes:
            X_prime[i:, f] = x_prime[f]
        else:
            X_prime[i, f] = x_prime[f]

    # Compute deltas in probs and preds
    probs_prime = model.predict_probs(X_prime)
    preds_prime = model.probs_to_predict(probs_prime)
    # Results
    return dict(
        prob=prob,
        # pred=pred,
        probs_deltas=probs_prime - prob,
        # probs_primes=probs_prime,
        preds_deltas=1 * (preds_prime != pred),
        # features_order=feat_order,
        # vals=vals[feat_order],
        # x_prime=X_prime[-1]
    )


def __feature_delta(
    features_span,
    features_trend,
    vals,
    epsilon_distribution,
    epsilon_proportional_to_attribution,
):
    features_delta = features_span.copy()
    nb_features = features_delta.shape[0]

    if epsilon_distribution == 'uniform':
        eps_ = np.random.rand(nb_features)
    elif epsilon_distribution == 'normal':
        eps_ = stats.truncnorm.rvs(a=0, b=np.inf, size=nb_features)
    else:
        eps_ = np.ones(nb_features)

    # Apply epsilon
    features_delta = features_delta * eps_ * (-features_trend)

    # Espilon variation proportional to the feature attribution
    if epsilon_proportional_to_attribution:
        features_delta = features_delta * vals

    return features_delta


def counterfactual_effects(
    xps_results,
    normalizer,
    model,
    features_trend,
    mode='std',
    phi=1,
    method='interv',
    keep_previous_changes=True,
    epsilon_distribution=None,
    epsilon_proportional_to_attribution=False,
    epsilon_sample=1,
):
    if epsilon_distribution is None and epsilon_sample != 1:
        epsilon_sample = 1
        logging.warning('epsilon_sample set to 1. Cannot have a sample without a epsilon_distribution set.')

    features_trend = np.array(features_trend)
    features_span = normalizer.feature_deviation(method=mode, phi=phi)

    effects_results = []
    for result in xps_results:
        vals = result[method]

        for _ in range(epsilon_sample):
            features_delta = __feature_delta(
                features_span=features_span,
                features_trend=features_trend,
                vals=vals,
                epsilon_distribution=epsilon_distribution,
                epsilon_proportional_to_attribution=epsilon_proportional_to_attribution,
            )
            x_prime = normalizer.single_shift_transform(result['x'], shift=features_delta, method=mode)
            effects_results.append(
                __counterfactual_effets(
                    x=result['x'],
                    prob=result['prob'],
                    pred=result['pred'],
                    vals=vals,
                    x_prime=x_prime,
                    keep_previous_changes=keep_previous_changes,
                    model=model,
                )
            )
    return effects_results


def all_counterfactual_effects(xps_results, *args, loaded=None, methods=None, **kwargs):
    if loaded is None:
        rets = {}
    else:
        rets = loaded
    if methods is not None:
        methods = list(set(get_methods_from_results(xps_results)) & set(methods))
    else:
        methods = get_methods_from_results(xps_results)
    for method in tqdm(methods, desc=str(kwargs['phi'])):
        if method not in rets:
            rets[method] = counterfactual_effects(xps_results, *args, method=method, **kwargs)
    return rets


# ██████╗  █████╗ ████████╗ █████╗     ████████╗██████╗  █████╗ ███████╗███████╗ ██████╗ ██████╗ ███╗   ███╗
# ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝██╔═══██╗██╔══██╗████╗ ████║
# ██║  ██║███████║   ██║   ███████║       ██║   ██████╔╝███████║███████╗█████╗  ██║   ██║██████╔╝██╔████╔██║
# ██║  ██║██╔══██║   ██║   ██╔══██║       ██║   ██╔══██╗██╔══██║╚════██║██╔══╝  ██║   ██║██╔══██╗██║╚██╔╝██║
# ██████╔╝██║  ██║   ██║   ██║  ██║       ██║   ██║  ██║██║  ██║███████║██║     ╚██████╔╝██║  ██║██║ ╚═╝ ██║
# ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝
#
def swapaxes_and_select(counter_effects_results, what, deviation_mode, phi, methods=None):
    selected_results = defaultdict(list)
    for effects_results in (counter_effects_results):
        deviation_results = effects_results[(deviation_mode, phi)]
        for method, results in deviation_results.items():
            if (methods is not None) and (method not in methods):
                continue
            selected_results[method].append(np.array([r[what] for r in results]))
    for method, results in (selected_results.items()):
        selected_results[method] = np.array(results)
    return selected_results


def join_results(nonaggr_res):
    """
        Return:
            dict of NumPy tot_nb_samples x nb_features
    """
    return {method: np.concatenate(nonaggr_res[method], axis=0) for method in nonaggr_res.keys()}


# ███████╗████████╗ █████╗ ████████╗███████╗
# ██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██╔════╝
# ███████╗   ██║   ███████║   ██║   ███████╗
# ╚════██║   ██║   ██╔══██║   ██║   ╚════██║
# ███████║   ██║   ██║  ██║   ██║   ███████║
# ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚══════╝
#


def compute_max_ks(nonaggr_res, apply=lambda x: x):
    """
        nonaggr_res : dict of list of NumPy
        apply : function to be applied to the NumPy arrays before the computation of the KS
    """
    max_ks = defaultdict(list)
    for method in nonaggr_res:
        for a, b in itertools.combinations(range(len(nonaggr_res[method])), 2):
            max_ks[method].append((np.abs(apply(nonaggr_res[method][a]) - apply(nonaggr_res[method][b]))).max())
    for method, vals in max_ks.items():
        if len(vals) > 0:
            max_ks[method] = np.array(vals).max()
    for method in nonaggr_res:
        if method not in max_ks:
            max_ks[method] = np.nan
    return dict(max_ks)


def compute_confidence_intervals(aggr_res, apply=lambda x: x):
    lower, upper = defaultdict(list), defaultdict(list)
    for method, results in aggr_res.items():
        for f in range(results.shape[1]):
            a = apply(results[:, f])
            mean = np.mean(a)
            inter = sp.stats.t.interval(0.95, len(a) - 1, loc=mean, scale=sp.stats.sem(a))
            lower[method].append(mean - inter[0])
            upper[method].append(inter[1] - mean)
    lower = {method: np.array(a) for method, a in lower.items()}
    upper = {method: np.array(a) for method, a in upper.items()}
    return lower, upper


# ██████╗ ██╗      ██████╗ ████████╗██╗  ██╗   ██╗
# ██╔══██╗██║     ██╔═══██╗╚══██╔══╝██║  ╚██╗ ██╔╝
# ██████╔╝██║     ██║   ██║   ██║   ██║   ╚████╔╝
# ██╔═══╝ ██║     ██║   ██║   ██║   ██║    ╚██╔╝
# ██║     ███████╗╚██████╔╝   ██║   ███████╗██║
# ╚═╝     ╚══════╝ ╚═════╝    ╚═╝   ╚══════╝╚═╝
#


def plotly_actionability(means, max_ks, lower, upper, what, mode, phi, top=None, fig=None):
    var_name = "XP"
    value_name = "Reduction of probability" if 'probs' in what else "Rate of prediction change"
    df = pd.DataFrame(means)

    # Add KS
    if max_ks is not None:
        df.rename(
            columns={
                method: method + f" (KS={str(np.round(max_ks[method], 4))[:6]}"
                for method in df.columns.values if max_ks is not None
            },
            inplace=True
        )

    df['top'] = df.index.values + 1
    if top is not None:
        df = df.iloc[:top]
    df = df.melt(id_vars=['top'], var_name=var_name, value_name=value_name)

    if lower is not None:
        df['lower'] = pd.DataFrame(lower).melt()['value'].values
    if upper is not None:
        df['upper'] = pd.DataFrame(upper).melt()['value'].values

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
        title=f"Effects of changing the top-x most important features on the"
        f"{'rate of prediction change' if 'preds' in what else 'predicted probability'}"
        f"<br>change type: {mode.upper()} /  Ɛ = {phi*100}%",
        xaxis_title='Number of top features changed (x)',
    )
    if 'preds' in what:
        fig.update_layout(yaxis_tickformat='.2%')
    fig.show()


# ███╗   ███╗ █████╗ ██╗███╗   ██╗    ██╗  ██╗ █████╗ ███╗   ██╗██████╗ ██╗     ███████╗███████╗
# ████╗ ████║██╔══██╗██║████╗  ██║    ██║  ██║██╔══██╗████╗  ██║██╔══██╗██║     ██╔════╝██╔════╝
# ██╔████╔██║███████║██║██╔██╗ ██║    ███████║███████║██╔██╗ ██║██║  ██║██║     █████╗  ███████╗
# ██║╚██╔╝██║██╔══██║██║██║╚██╗██║    ██╔══██║██╔══██║██║╚██╗██║██║  ██║██║     ██╔══╝  ╚════██║
# ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║    ██║  ██║██║  ██║██║ ╚████║██████╔╝███████╗███████╗███████║
# ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝╚══════╝
#


def plot_actionability(
    what,
    mode,
    aggregation=np.mean,
    methods=None,
    counter_effects_results=None,
    counter_effects_results_ps=None,
):
    """"
    Arguments:
        what : the result to be plotted
            'preds_deltas' or 'probs_deltas'
        mode : the shift mode
            'mad', 'std' or 'percshift'
        aggregation : aggregation function (mean or median)
    """
    # Depending on the type of shift we use different metrics
    if mode in ['std', 'mad']:
        cer = counter_effects_results
    elif mode == 'percshift':
        cer = counter_effects_results_ps

    # Sort the phis before looping
    for phi, mode_ in sorted([(phi, mode_) for mode_, phi in cer[0].keys()]):
        if mode_ != mode:
            continue

        # Select results
        # dict (of methods) of list (of samples) of NumPy (nb_samples x nb_features)
        nonaggr_res = swapaxes_and_select(cer, what, mode, phi, methods=methods)

        # Aggregate results
        # dict (of methods) of NumPy (tot_nb_samples x nb_features)
        aggr_res = join_results(nonaggr_res)

        # Compute means
        means = {method: aggregation(results, axis=0) for method, results in aggr_res.items()}

        # Compute KS divergence
        max_ks = compute_max_ks(nonaggr_res, apply=lambda x: aggregation(x, axis=0))

        # Computer confidence intervals
        if aggregation == np.mean:
            lower, upper = compute_confidence_intervals(aggr_res)
        else:
            lower, upper = None, None

        # Plot
        plotly_actionability(
            means=means,
            max_ks=max_ks,
            lower=lower,
            upper=upper,
            what=what,
            mode=mode,
            phi=phi,
        )