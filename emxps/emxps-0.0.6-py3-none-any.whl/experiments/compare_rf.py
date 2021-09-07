from collections import defaultdict
import itertools
import logging
from typing import Union, Iterable, Dict, List, Any
import numpy as np
import pandas as pd
import scipy as sp
#pylint: disable=unused-import
import scipy.stats
#pylint: enable=unused-import
import plotly.express as px

from emutils.utils import notebook_fullwidth
from emutils.utils import import_tqdm
from emutils.utils import np_sample

from ..xps import TreeExplainer
from ..xps import compute_xps_batch
from ..xps import filter_only_explanations

tqdm = import_tqdm()

# ███████╗██╗  ██╗███████╗ ██████╗██╗   ██╗████████╗██╗ ██████╗ ███╗   ██╗
# ██╔════╝╚██╗██╔╝██╔════╝██╔════╝██║   ██║╚══██╔══╝██║██╔═══██╗████╗  ██║
# █████╗   ╚███╔╝ █████╗  ██║     ██║   ██║   ██║   ██║██║   ██║██╔██╗ ██║
# ██╔══╝   ██╔██╗ ██╔══╝  ██║     ██║   ██║   ██║   ██║██║   ██║██║╚██╗██║
# ███████╗██╔╝ ██╗███████╗╚██████╗╚██████╔╝   ██║   ██║╚██████╔╝██║ ╚████║
# ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
#

# def generate_perturbations(point, n, norm_method, normalizer, features_trend):
#     for d in [1, -1]:
#         for i in range(n):
#             shift = normalizer.feature_deviation(
#                 phi=i / n,
#                 method=norm_method,
#             ) * features_trend * np.random.uniform(size=len(point)) * d
#             ppoint = normalizer.single_shift_transform(
#                 point,
#                 shift=shift,
#                 method=norm_method,
#             )
#             yield ppoint


# %%
def generate_perturbations(point, n, norm_method, normalizer, features_trend, m=1):
    perturbed_points = []
    for d in [1, -1]:
        for i in range(1, n + 1):
            shifts = normalizer.feature_deviation(
                phi=i / n,
                method=norm_method,
            ) * features_trend * np.random.uniform(size=(m, len(point))) * d
            points_prime = normalizer.shift_transform(
                np.tile(point, (m, 1)),
                shifts=shifts,
                method=norm_method,
            )
            if m == 1:
                perturbed_points.extend(points_prime)
            else:
                perturbed_points.append(points_prime)
    return np.array(perturbed_points)


# %%
def generate_explanations_from_refpoints(model, ref_points, X, explainers_names=None, desc=None):
    """Generate explanations of samples in X with SHAP fed with the reference points ref_points

    Args:
        model (Wrapper): XGB Model Wrapper
        ref_points (Iterable): Reference points
        X (np.ndarray): NumPy dataset
        explainers_names (List[Any], optional): Names of the explainers. Defaults to None (range from 0 to len(ref_points)).

    Returns:
        List[Dict[Any, np.ndarray]]: Explanations
    """
    # If no names are passed for the explainers then I just use incremental numbers
    if explainers_names is None:
        explainers_names = list(range(len(ref_points)))
    assert len(explainers_names) == len(ref_points)

    # Create the explainers with the reference points
    explainers = {
        i: TreeExplainer(model, data=ref.reshape(1, -1), feature_perturbation='interventional')
        for i, ref in zip(explainers_names, ref_points)
    }

    # Generate the explanations
    xps = compute_xps_batch(
        X,
        model=model,
        explainers=explainers,
        debug=False,
        soft_debug=False,
        desc=desc if desc is not None else "XPS",
    )

    return xps


def compute_ranks_from_xps(xps, desc='Ranks'):
    return np.array(
        [{k: sp.stats.rankdata(v)
          for k, v in r.items()} for r in tqdm(filter_only_explanations(xps), desc=desc)]
    )


def __compare_ranks(r, s):
    return {
        'Ranks Kendall Tau-B': sp.stats.kendalltau(r, s).correlation,
        # 'Stuart-Kendall Tau-C': sp.stats.kendalltau(rau, rbu, variant='c')
        'Ranks Spearman Rho': sp.stats.spearmanr(r, s).correlation,
        'Ranks L0 Norm': ((r - s) != 0).sum(),
        'Ranks L1 Norm': np.abs((r - s)).sum(),
        'Ranks L2 Norm': np.linalg.norm(r - s),
    }


def __compare_xps(r, s):
    return {
        'XP Spearman Rho': sp.stats.spearmanr(r, s).correlation,
        'XP L0 Norm': ((r - s) != 0).sum(),
        'XP L1 Norm': np.abs((r - s)).sum(),
        'XP L2 Norm': np.linalg.norm(r - s),
    }


def compare_ranks_by_explainer(
    ranks: Iterable,
    compare_mode='firt_vs_all',
    compare_to: Union[list, None, str] = None,
    compare_from: Union[list, None] = None,
    nb_comparison: Union[None, int] = 10,
    random_state: int = 0,
):
    """Compare ranks of the same sample with different explainers

    The method support two modes:
        - specifying 2 sets of explainers: compare_from and compare_to (Default)
        - random comparison : using nb_comparison

    Args:
        ranks (Iterable): Ranks of the explanations
        compare_to (Union[list, None, str], optional): Explainers to be compared to. Defaults to None (compare_to=[0]).
        compare_from (Union[list, None], optional): Explainers to be compared from. Defaults to None (compare_from = range(nb_explainers)).
        nb_comparison (Union[None, int], optional): Number of random comparisons per explainer. Defaults to 10.
        random_state (int, optional): Defaults to 0. Used only if compare_mode == 'random'.

    Returns:
        Dict[
            rank_comp_metric_name : str, 
            Dict[
                (explainer_a, explainer_b) : (str, str), 
                List[metric_value : float] (for all samples)
            ]
        ]: Ranks comparison metrics results
    """
    exp_names = list(ranks[0].keys())

    # Combinations that we want to look at
    if compare_mode == 'firt_vs_all':
        combs = [(exp_names[0], j) for j in exp_names[1:]]
    elif compare_mode == 'to_vs_from':
        assert compare_from is not None and compare_to is not None
        combs = [(i, j) for i in compare_to for j in compare_from if i < j]
    elif compare_mode == 'all':
        combs = list(itertools.combinations(exp_names, 2))
    elif compare_mode == 'random':
        if nb_comparison > len(exp_names):
            logging.warning(
                'Random sampling of ranks is more expensive than comparing all combinations."\
                    "Consider setting compare_mode = \'all\''
            )
        combs = list(
            set(
                [
                    (a, b) for a in exp_names
                    for b in np_sample(exp_names, replace=True, n=nb_comparison, seed=random_state + a) if a != b
                ]
            )
        )
    else:
        raise ValueError('Invalid compare_mode.')

    # Empty dict
    corrs = defaultdict(lambda: defaultdict(list))
    for _, r in enumerate(tqdm(ranks, desc='Correlations')):
        for a, b in combs:
            ra, rb = r[a], r[b]
            # rau = np.unique(ra, return_index=True)[1]
            # rbu = np.unique(rb, return_index=True)[1]
            for met, val in __compare_ranks(ra, rb).items():
                corrs[met][(a, b)].append(val)
    # Transform defaultdict to dict
    corrs = {k: dict(v) for k, v in corrs.items()}
    return corrs


# %%
def compare_ranks_by_sample(
    ranks: Iterable[Dict[Any, np.ndarray]],
    compare_mode='random',
    xps: Iterable[Dict[Any, np.ndarray]] = None,
    nb_comparison: int = None,
    random_state: int = 0,
    desc: str = 'Correlations',
) -> Dict[str, Dict[Any, list]]:
    """Compare the ranks of the same explainer by sample (randomly drawing the sample to be compared)

    Args:
        ranks (Iterable[Dict[Any, np.ndarray]]): Ranks
        compare_mode (str, optional): Comparison mode. Default to 'random'.
            If compare_mode = 'random' then a sample of pair of samples is drawn and pairwise metrics are computed.
            If compare_mode = 'first_vs_all' then the first sample ranks are compared against all the others.
        nb_comparison (int): Number of random comparisons between samples for the same explainer. Used only if compare_mode = 'random'.
        random_state (int, optional): Defaults to 0.  Used only if compare_mode = 'random'.

    

    Returns:
        Dict[
            metric_name : str, 
            Dict[
                explainer_name : Any, 
                metrics : List[float]
            ]
        ]: Ranks comparison metrics results
    """

    # Empty dict
    corrs = defaultdict(lambda: defaultdict(list))

    if compare_mode == 'random':
        # Number of comparison per sample
        n = int(max(1, nb_comparison / len(ranks)))

        # Do the comparisons
        for i, r in enumerate(tqdm(ranks, desc=desc)):
            for j in np_sample(len(ranks), n=n, seed=random_state + i, safe=True):
                if i != j:
                    s = ranks[j]
                    for explainer_name in (set(r.keys()) & set(s.keys())):
                        re, se = r[explainer_name], s[explainer_name]
                        # Compute metrics
                        for met, val in __compare_ranks(re, se).items():
                            corrs[met][explainer_name].append(val)

    elif compare_mode == 'first_vs_all':

        def __compare_firt_vs_all(results, fun):
            # We get the first sample explanation
            r0 = results[0]
            # We compare against all the others
            for r in tqdm(results[1:], desc=desc):
                for explainer_name in (set(r.keys()) & set(r0.keys())):
                    re, se = r[explainer_name], r0[explainer_name]
                    # Compute metrics
                    for met, val in fun(re, se).items():
                        corrs[met][explainer_name].append(val)

        # Compare ranks
        __compare_firt_vs_all(ranks, __compare_ranks)
        # And in case there are, also explanations themselves
        if xps is not None:
            __compare_firt_vs_all(xps, __compare_xps)

    else:
        raise ValueError('Invalid comparison mode.')

    # Transform defaultdict to dict
    corrs = {k: dict(v) for k, v in corrs.items()}
    return corrs


def compute_stat_on_corrs_by_sample(corrs, stat=np.mean):
    """Compute statistics of the of the results of `compare_ranks_by_sample` function

    Args:
        corrs ([type]): Results from `compare_ranks_by_sample`
        stat (lambda, optional): A function to run over an np.ndarray. Defaults to np.mean.

    Returns:
        Dict[
            result_metric : str, 
            Dict[ 
                name_of_the_result : Any, 
                float
            ]
        ]: Statistics of the results
    """
    variances = defaultdict(dict)
    for metric, results in corrs.items():
        for k, ll in results.items():
            variances[metric][k] = stat(np.array(ll))
    return dict(variances)


def concatenate_corrs(corrs_list):
    corrs_ = defaultdict(dict)
    for corrs in corrs_list:
        for metric, results in corrs.items():
            corrs_[metric].update(results)
    return corrs_


def compare_horizontally(model, X, reference_points, groups):
    reference_groups = []
    all_corrs = []
    for i, (rf_points, group_name) in enumerate(zip(reference_points, groups)):
        # Generate explainers of Baseline-SHAP with different reference points
        # and compute explanations
        xps = generate_explanations_from_refpoints(
            X=X,
            model=model,
            ref_points=rf_points,
            explainers_names=[group_name + "_" + str(j) for j in range(len(rf_points))]
        )
        # Transform feature attribution into rankings
        ranks = compute_ranks_from_xps(xps)

        # Compute correlations measures
        corrs = compare_ranks_by_explainer(ranks, compare_mode='all')
        all_corrs.append(corrs)

        # Add the group names
        reference_groups.extend([group_name] * len(corrs[list(corrs.keys())[0]]))

    # Concatenate all results
    corrs = concatenate_corrs(all_corrs)

    return corrs, reference_groups


def compare_vertically(model, X, reference_points):
    # Generate explainers of Baseline-SHAP with different reference points
    # and compute explanations
    xps = generate_explanations_from_refpoints(
        X=X,
        model=model,
        ref_points=reference_points,
    )
    # Transform feature attribution into rankings
    ranks = compute_ranks_from_xps(xps)

    # Compute correlations measures
    corrs = compare_ranks_by_explainer(ranks)

    return corrs


# ██████╗ ██╗      ██████╗ ████████╗
# ██╔══██╗██║     ██╔═══██╗╚══██╔══╝
# ██████╔╝██║     ██║   ██║   ██║
# ██╔═══╝ ██║     ██║   ██║   ██║
# ██║     ███████╗╚██████╔╝   ██║
# ╚═╝     ╚══════╝ ╚═════╝    ╚═╝
# %%


def plot_corrs_single(
    corrs,
    reference_groups=None,
    title='AAR-SHAP explanations vs. other baseline SHAP explanations',
    width=2000,
    height=400,
):

    # Set the notebook to maximum width
    notebook_fullwidth()

    # For each metric plot a bar plot
    for metric, results in corrs.items():
        keys = [str(k) for k in results.keys()]
        vals = [np.array(v).mean() for v in results.values()]
        rf_name = 'Ref. Point'
        group_name = 'Group'
        df = pd.DataFrame({
            rf_name: keys,
            metric: vals,
            group_name: reference_groups,
        })
        if reference_groups is not None:
            df[group_name] = reference_groups
            px.bar(
                df,
                x=rf_name,
                y=metric,
                color=group_name,
                width=width,
                height=height,
                title=title,
            ).show()

        else:
            px.bar(
                df,
                x=rf_name,
                y=metric,
                width=width,
                height=height,
                title=title,
            ).show()


def plot_reference_probs(reference_probs, reference_groups):
    df = pd.DataFrame(reference_probs, columns=['Probability'])
    df['G'] = ['Original Reference Point'] + reference_groups
    df['x'] = df.index.values
    px.scatter(df, y='Probability', color='G', x='x').show()


# %%
