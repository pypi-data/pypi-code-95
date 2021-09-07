import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels
import statsmodels.stats.proportion

from emutils.utils import display
from ..xps import get_methods_from_results, get_counter_methods_from_results

# ███████╗██╗  ██╗███████╗ ██████╗██╗   ██╗████████╗██╗ ██████╗ ███╗   ██╗
# ██╔════╝╚██╗██╔╝██╔════╝██╔════╝██║   ██║╚══██╔══╝██║██╔═══██╗████╗  ██║
# █████╗   ╚███╔╝ █████╗  ██║     ██║   ██║   ██║   ██║██║   ██║██╔██╗ ██║
# ██╔══╝   ██╔██╗ ██╔══╝  ██║     ██║   ██║   ██║   ██║██║   ██║██║╚██╗██║
# ███████╗██╔╝ ██╗███████╗╚██████╗╚██████╔╝   ██║   ██║╚██████╔╝██║ ╚████║
# ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
#

# Empty and non-positive


def count_empty(xps_results):
    return {
        **{
            method: np.array([result[method] is None for result in xps_results])
            for method in get_methods_from_results(xps_results)
        }
    }


def count_nonpositive(xps_results):
    return {
        method: [(result[method] <= 0).sum() if result[method] is not None else np.nan for result in xps_results]
        for method in get_methods_from_results(xps_results)
    }


# Zeros


def count_shapzeros(xps_results):
    return {
        method: [(result[method] == 0).sum() if result[method] is not None else np.nan for result in xps_results]
        for method in get_methods_from_results(xps_results)
    }


# Size of counterfactuals set


def count_countersize(xps_results):
    return {
        method: [len(result[method + '_X']) if result[method] is not None else np.nan for result in xps_results]
        for method in get_counter_methods_from_results(xps_results)
    }


def count_shappositive(xps_results):
    return {
        method: np.array(
            [
                1 * (result[method] > 0) if result[method] is not None else [np.nan] * len(result['x'])
                for result in xps_results
            ]
        )
        for method in get_methods_from_results(xps_results)
    }


# Missingness


def count_missing(xps_results, maxval):
    return np.array([(result['x_nonrecoded'] > maxval) for result in xps_results])


def count_missing_positive(xps_results, maxval):
    missing_counts = count_missing(xps_results, maxval)
    return {
        method: np.array(
            np.array(
                [
                    missing_mask * (result[method] > 0) if result[method] is not None else [np.nan] * len(result['x'])
                    for result, missing_mask in zip(xps_results, missing_counts)
                ]
            )
        )
        for method in get_methods_from_results(xps_results)
    }


# ██████╗ ██╗      ██████╗ ████████╗███████╗
# ██╔══██╗██║     ██╔═══██╗╚══██╔══╝██╔════╝
# ██████╔╝██║     ██║   ██║   ██║   ███████╗
# ██╔═══╝ ██║     ██║   ██║   ██║   ╚════██║
# ██║     ███████╗╚██████╔╝   ██║   ███████║
# ╚═╝     ╚══════╝ ╚═════╝    ╚═╝   ╚══════╝
#


def plot_missing(missing, missing_positive):
    """Plot the results of the 'missing' experiment

    Args:
        missing (list): List of results from the experiment (different random seeds)
        missing_positive (list): List of results from the experiment (different random seeds)
    """
    missing = np.concatenate(missing, axis=0)
    missing_positive = {
        method: np.concatenate([np.nan_to_num(result[method], 0) for result in missing_positive], axis=0)
        for method in get_methods_from_results(missing_positive)
    }
    missing_n = len(missing)
    nb_missings = missing.sum()
    nb_missings_positive = {method: results.sum() for method, results in missing_positive.items()}

    fig = go.Figure(
        data=[
            go.Bar(
                name='Total',
                x=['total'],
                y=[nb_missings],
            ),
            go.Bar(
                name='Methods',
                x=list(nb_missings_positive.keys()),
                y=list(nb_missings_positive.values()),
            ),
        ]
    )
    fig.update_layout(
        title=f'Number of missing/special values that are returned in explanations (n={missing_n})',
        xaxis_title="",
        yaxis_title="count (lower is better)",
    )
    fig.show()


def plot_countersize(counts, methods=None):
    counts = {
        method: sum([count[method] for count in counts], [])
        for method in get_methods_from_results(counts[0]) if methods is None or (method in methods)
    }
    var_name, value_name = 'Method', "Number of counterfactuals fed to SHAP"
    fig = px.histogram(
        pd.DataFrame(counts).melt(var_name=var_name, value_name=value_name),
        x=value_name,
        facet_row=var_name,
        nbins=75,
        height=len(counts) * 150
    )
    fig.update_layout(title="Size of the counterfactuals dataset for non-empty explanations")
    fig.show()


def plot_empty(counts_empty, counts_nonpositive, methods=None):
    def __compute_percentage_and_confidence(counts):
        confidence = {
            method: statsmodels.stats.proportion.proportion_confint(count=a.sum(), nobs=a.shape[0], alpha=.05)
            for method, a in counts.items()
        }

        # Trasform interval to difference
        confidence = {method: b - a for method, (a, b) in confidence.items()}

        # Occurence percentage
        counts = {method: a.sum() / a.shape[0] for method, a in counts.items()}

        # Return occurence and confidence
        return pd.DataFrame([counts, confidence]).T

    def __process_empty(counts):
        counts = {
            method: 1 * np.concatenate([e[method] for e in counts])
            for method in counts[0].keys() if methods is None or (method in methods)
        }

        nb_samples_empty = len(counts[list(counts.keys())[0]])
        percentage_empty = __compute_percentage_and_confidence(counts)

        return percentage_empty, nb_samples_empty

    def __process_nonpositive(counts):
        counts = {
            method: 1 * np.concatenate([1 * (e[method].sum(axis=1) == 0) for e in counts])
            for method in counts[0].keys() if methods is None or (method in methods)
        }
        nb_samples_nonpositive = len(counts[list(counts.keys())[0]])
        percentage_nonpositive = __compute_percentage_and_confidence(counts)

        return percentage_nonpositive, nb_samples_nonpositive

    def __plot_empty(percentage_empty, nb_samples_empty, percentage_nonpositive, nb_samples_nonpositive):
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                name='non-computable',
                x=percentage_empty.index.values,
                y=percentage_empty[0].values,
                error_y=dict(type='data', array=percentage_empty[1].values),
            )
        )
        fig.add_trace(
            go.Bar(
                name='non-existing',
                x=percentage_nonpositive.index.values,
                y=percentage_nonpositive[0].values,
                error_y=dict(type='data', array=percentage_nonpositive[1].values),
            )
        )
        fig.update_layout(
            yaxis_tickformat='.2%',
            xaxis_title='Method',
            yaxis_title="Percentage of explanations",
        )
        fig.update_layout(
            barmode='group',
            title=f"Rate of non-computability or non-existence (no attribution > 0)"
            f"<br> n = {nb_samples_empty} / {nb_samples_nonpositive} (Clopper-Pearson)",
        )
        fig.show()

        display(
            pd.DataFrame(
                [percentage_empty[0].values, percentage_nonpositive[0].values],
                index=['non-computable', 'non-existing'],
                columns=percentage_empty.index.values
            ).apply(lambda s: s.apply(lambda x: f"{x*100:.2f}%")).T
        )

    percentage_empty, nb_samples_empty = __process_empty(counts_empty)
    percentage_nonpositive, nb_samples_nonpositive = __process_nonpositive(counts_nonpositive)

    return __plot_empty(percentage_empty, nb_samples_empty, percentage_nonpositive, nb_samples_nonpositive)


def plot_positive(counts, methods=None):
    counts = {
        method: 1 * np.concatenate([1 * (e[method].sum(axis=1)) for e in counts])
        for method in counts[0].keys() if methods is None or (method in methods)
    }
    var_name, value_name = 'Method', "Number of features with positive attribution"
    fig = px.histogram(
        pd.DataFrame(counts).melt(var_name=var_name, value_name=value_name),
        x=value_name,
        facet_row=var_name,
        color=var_name,
        nbins=150,
        height=200 * len(counts)
    )
    fig.update_layout(title="Size of the explanations: Number of features w/att > 0")
    fig.show()
