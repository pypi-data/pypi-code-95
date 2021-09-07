import numpy as np
import pandas as pd
import scipy as sp
from tqdm import tqdm
import plotly.express as px
import plotly.figure_factory as ff

from emutils.rbo import RankingSimilarity

from ..xps import get_methods_from_results


def compute_sensitivity(xps_results, xps_results_epsilon, method, rank_method='average'):
    for r, s in zip(xps_results, xps_results_epsilon):
        # Get the attributions
        if (method not in r) or (method not in s):
            return np.nan
        vals = r[method]
        vals_epsilon = s[method]

        # Compute the Kendall-Tau distance between rankings
        if (vals is not None) and (vals_epsilon is not None):
            yield sp.stats.kendalltau(
                sp.stats.rankdata(vals, method=rank_method), sp.stats.rankdata(vals_epsilon, method=rank_method)
            )


def compute_all_sensitivity(xps_results, *args, loaded=None, **kwargs):
    if loaded is None:
        rets = {}
    else:
        rets = loaded
    for method in tqdm(get_methods_from_results(xps_results)):
        if method not in rets:
            rets[method] = np.array(list(compute_sensitivity(xps_results, *args, method=method, **kwargs)))
    return rets


# %%


def pairwise_sensistivity(xps_results, metric='kendalltau', rank_method='average', p=.875):
    methods = sorted(list(get_methods_from_results(xps_results)))
    res = []
    for result in xps_results:
        if metric == 'kendalltau':
            ranks = np.array([sp.stats.rankdata(result[m], method=rank_method) for m in methods])
            res.append(
                sp.spatial.distance.
                squareform(sp.spatial.distance.pdist(ranks, (lambda x, y: sp.stats.kendalltau(x, y).correlation))) +
                np.diag(np.ones(len(methods)))
            )
        elif metric == 'rbo':
            rank_args = np.array([np.flip(np.argsort(result[m])) for m in methods])
            res.append(
                sp.spatial.distance.squareform(
                    sp.spatial.distance.pdist(rank_args, (lambda x, y: RankingSimilarity(x, y).rbo(p=p, ext=True)))
                ) + np.diag(np.ones(len(methods)))
            )
        else:
            raise ValueError('Invalid metric.')

    return methods, np.array(res)


def plot_pairwise_sensitivity(methods, psens):
    df = pd.concat(
        [
            pd.DataFrame(
                r, columns=[m.replace('shap_', '') for m in methods], index=[m.replace('shap_', '') for m in methods]
            ) for r in psens
        ]
    )
    df['A'] = df.index.values
    df = df.melt(var_name='B', id_vars='A')
    fig = px.histogram(df, x='value', facet_row='A', facet_col='B', title='Pairwise Sensitivity')
    fig.show()


def plot_single_pairwise_sensitivity(
    methods,
    psen,
    title='Pairwise Sensitivity',
    width=900,
    height=500,
):
    z_text = np.around(psen, decimals=2)

    fig = ff.create_annotated_heatmap(
        z=psen,  # Values
        x=methods,  # X-axis labels
        y=methods,  # Y-axis labels
        annotation_text=z_text,
        colorscale='RdBu',
        hoverinfo='z',
        zmid=.5,
    )

    # Make text size smaller
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].font.size = 10

    fig.update_layout(title=title, margin=dict(t=135), height=height, width=width)

    fig.show()


# %%
