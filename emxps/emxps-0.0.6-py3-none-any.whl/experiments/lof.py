import itertools
from collections import defaultdict
import numpy as np
import pandas as pd
import plotly.express as px
import scipy as sp
#pylint: disable=unused-import
import scipy.stats
#pylint: enable=unused-import

from tqdm import tqdm

from emutils.geometry.lof import NormalizedLOF

# ███████╗██╗  ██╗███████╗ ██████╗██╗   ██╗████████╗██╗ ██████╗ ███╗   ██╗
# ██╔════╝╚██╗██╔╝██╔════╝██╔════╝██║   ██║╚══██╔══╝██║██╔═══██╗████╗  ██║
# █████╗   ╚███╔╝ █████╗  ██║     ██║   ██║   ██║   ██║██║   ██║██╔██╗ ██║
# ██╔══╝   ██╔██╗ ██╔══╝  ██║     ██║   ██║   ██║   ██║██║   ██║██║╚██╗██║
# ███████╗██╔╝ ██╗███████╗╚██████╗╚██████╔╝   ██║   ██║╚██████╔╝██║ ╚████║
# ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
#


def compute_local_outlier_factor(xps_results, method, normalizer, normalize, lof_only=True, **lof_params):

    lof = NormalizedLOF(normalizer=normalizer, method=normalize, **lof_params)

    # Compute the distancelo
    def k_nearest_distance(xps_results):
        for result in xps_results:
            X__ = result[method + '_X']
            if X__ is not None and len(X__) > 0:
                # Average distance between the n-neighbors
                # shape = X__.shape[0]
                yield lof.kneighbors_distance(X__)

    # Compute the distancelo
    def lof_factor(xps_results):
        for result in xps_results:
            X__ = result[method + '_X']
            if X__ is not None and len(X__) > 0:
                # LOF of the counterfactuals
                # shape = X__.shape[0]
                yield lof.local_outlier_factor(X__)

    # Compute LOF
    all_lof = np.array(list(lof_factor(tqdm(xps_results, desc='LOF'))))

    # If requested we compute also the KNN distance
    if lof_only:
        all_knn = None
    else:
        all_knn = np.array(list(k_nearest_distance(tqdm(xps_results, desc='K-N Avg. Dist.'))))

    # Return resultss
    return all_knn, all_lof


# ██████╗  █████╗ ████████╗ █████╗     ████████╗██████╗  █████╗ ███████╗███████╗ ██████╗ ██████╗ ███╗   ███╗
# ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝██╔═══██╗██╔══██╗████╗ ████║
# ██║  ██║███████║   ██║   ███████║       ██║   ██████╔╝███████║███████╗█████╗  ██║   ██║██████╔╝██╔████╔██║
# ██║  ██║██╔══██║   ██║   ██╔══██║       ██║   ██╔══██╗██╔══██║╚════██║██╔══╝  ██║   ██║██╔══██╗██║╚██╔╝██║
# ██████╔╝██║  ██║   ██║   ██║  ██║       ██║   ██║  ██║██║  ██║███████║██║     ╚██████╔╝██║  ██║██║ ╚═╝ ██║
# ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝
#


def swap_axes(robust_results_per_method):
    hists = defaultdict(lambda: defaultdict(list))

    # Iterate over the files and load the results
    for method, results_per_metric in robust_results_per_method.items():
        for met, metric_results in results_per_metric.items():
            for result in metric_results:
                lof = result[1]
                hist = np.concatenate(lof)
                hists[method][met].append(hist)

    return hists


# ███████╗████████╗ █████╗ ████████╗███████╗
# ██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██╔════╝
# ███████╗   ██║   ███████║   ██║   ███████╗
# ╚════██║   ██║   ██╔══██║   ██║   ╚════██║
# ███████║   ██║   ██║  ██║   ██║   ███████║
# ╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚══════╝
#


def compute_ks_max(nonaggr_res):
    max_ks = defaultdict(list)
    for met, rl in nonaggr_res.items():
        for a, b in itertools.combinations(rl, 2):
            max_ks[met].append(sp.stats.ks_2samp(a, b).statistic)
    for met, vals in max_ks.items():
        if len(vals) > 0:
            max_ks[met] = np.array(vals).max()
    for met in nonaggr_res:
        if met not in max_ks:
            max_ks[met] = np.nan

    return max_ks

    # for met, rl in nonaggr_res.items():
    #     for a, b in itertools.combinations(rl, 2):
    #         means[method][met].append(a.mean() - b.mean())
    #         stds[method][met].append(a.std() - b.std())


# ██████╗ ██╗      ██████╗ ████████╗
# ██╔══██╗██║     ██╔═══██╗╚══██╔══╝
# ██████╔╝██║     ██║   ██║   ██║
# ██╔═══╝ ██║     ██║   ██║   ██║
# ██║     ███████╗╚██████╔╝   ██║
# ╚═╝     ╚══════╝ ╚═════╝    ╚═╝
#


# %%
def plotly_lof_per_method(aggr_res, max_ks, method):
    title = 'Local Outlier Factor (LOF)'
    var_name, value_name = ' ', 'LOF'

    # Build dict for DF
    melted = {
        f"{metric} (K={K}) / mu={str(np.round(result.mean(), 2))[:4]}, "
        f"sig={str(np.round(result.std(), 2))[:4]} / KS_max = {str(np.round(max_ks[(K, metric)], 3))[:5]}": result
        for (K, metric), result in aggr_res.items()
    }

    # Pad with nan to create the DF
    # Different metrics might have been run on a different number of samples
    max_nb = max([len(result) for result in melted.values()])
    for met in melted.keys():
        if len(melted[met]) < max_nb:
            melted[met] = np.concatenate([melted[met], np.array([np.nan] * (max_nb - len(melted[met])))])

    # DataFrame
    melted = pd.DataFrame(melted).melt(var_name=var_name, value_name=value_name)

    # Plot
    fig = px.histogram(
        melted,
        x=value_name,
        title=title + ' - ' + method,
        nbins=1000,
        color=var_name,
        barmode="overlay",
    )
    fig.show()


# ███╗   ███╗ █████╗ ██╗███╗   ██╗    ██╗  ██╗ █████╗ ███╗   ██╗██████╗ ██╗     ███████╗███████╗
# ████╗ ████║██╔══██╗██║████╗  ██║    ██║  ██║██╔══██╗████╗  ██║██╔══██╗██║     ██╔════╝██╔════╝
# ██╔████╔██║███████║██║██╔██╗ ██║    ███████║███████║██╔██╗ ██║██║  ██║██║     █████╗  ███████╗
# ██║╚██╔╝██║██╔══██║██║██║╚██╗██║    ██╔══██║██╔══██║██║╚██╗██║██║  ██║██║     ██╔══╝  ╚════██║
# ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║    ██║  ██║██║  ██║██║ ╚████║██████╔╝███████╗███████╗███████║
# ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝╚══════╝
#


def plot_lof_hists(results):

    # non_aggr_results = dict (per method) of dict (per metric) of list (per 1,000 sample) of LOF (float)
    all_results = swap_axes(results)

    for method, nonaggr_res in all_results.items():
        # method_results = dict (per metric) of list (per 1,000 sample) of LOF (float)

        aggr_res = {met: np.concatenate(res_list) for met, res_list in nonaggr_res.items()}

        # Compute KS-Statistics
        max_ks = compute_ks_max(nonaggr_res)

        # Plot results
        plotly_lof_per_method(aggr_res, max_ks=max_ks, method=method)


# %%
