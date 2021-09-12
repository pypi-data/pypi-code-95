"""
Visualization
-------------
The ``maica.util.visualization`` module provides various visualization tools for dataset analysis and evaluations.
This module was implemented based on ``matplotlib`` to serve a unified interface.
"""


import numpy
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.manifold import SpectralEmbedding
from maica.core.env import *
from maica.data.base import Dataset
from maica.util.analysis import get_error_dist


def plot_target_dist(fig_name: str,
                     dataset: Dataset,
                     n_bins: int = 10,
                     font_size: int = 16):
    """
    Plot a histogram of the target values of ``dataset``.
    The histogram is saved as an image file in ``fig_name``.

    :param fig_name: (*str*) A name of the image file storing the histogram of the target values.
    :param dataset: (*maica.data.base.Dataset*) The dataset object containing the target values.
    :param n_bins: (*int, optional*) The number of bins in the histogram (*default* = 10).
    :param font_size: (*int, optional*) The size of text in the generated figure (*default* = 16).
    """

    targets = dataset.y
    y_min = numpy.min(targets)
    y_max = numpy.max(targets)
    label_bins = numpy.linspace(y_min, y_max, n_bins + 1)

    plt.tight_layout()
    plt.rcParams.update({'font.size': font_size})
    plt.title('Histogram of Target Distribution')
    plt.xlabel('Target range')
    plt.ylabel('# of data')
    plt.hist(targets, label_bins, edgecolor='black', zorder=2)
    plt.grid(linestyle='--')
    plt.savefig(fig_name, bbox_inches='tight', dpi=500)
    plt.close()


def plot_error_dist(fig_name: str,
                    dataset: Dataset,
                    preds: numpy.ndarray,
                    font_size: int = 16):
    """
    Plot a distribution of prediction errors.
    The prediction errors for each target range are calculated based on mean absolute error as:

    .. math::
        error = \\frac{1}{N_i}\sum_{j=1}^{N_i}|y_j - y_j^{'}|,

    where :math:`N_i` is the number of data points in the :math:`i^{th}` target range,
    :math:`y_j` is the target value of the :math:`j^{th}` data in the :math:`i^{th}` target range,
    and :math:`y_{j}^{'}` is the predicted value of the :math:`j^{th}` data.

    :param fig_name: (*str*) A name of the image file storing the error distribution.
    :param dataset: (*maica.data.base.Dataset*) The dataset object containing the target values.
    :param preds: (*numpy.ndarray*) Prediction results.
    :param font_size: (*int, optional*) The size of text in the generated figure (*default* = 16).
    """

    errors, labels = get_error_dist(dataset.y, preds)
    labels = [(labels[i] + labels[i + 1]) / 2 for i in range(0, len(labels) - 1)]
    width_bar = (labels[1] - labels[0])

    plt.tight_layout()
    plt.rcParams.update({'font.size': font_size})
    plt.title('Error Distribution for Each Target range')
    plt.xlabel('Target range')
    plt.ylabel('Mean of prediction errors')
    plt.bar(labels, errors, edgecolor='black', width=width_bar, zorder=2)
    plt.grid(linestyle='--')
    plt.savefig(fig_name, bbox_inches='tight', dpi=500)
    plt.close()


def plot_pred_result(fig_name: str,
                     dataset: object,
                     preds: numpy.ndarray,
                     font_size: int = 16,
                     min_val: float = None,
                     max_val: float = None):
    """
    Draw a scatter plot of the prediction results in ``preds``.
    The X and Y axes are drawn by the true target values in ``dataset`` and the predicted values in ``preds``, respectively.

    :param fig_name: (*str*) A name of the image file storing the scatter plot.
    :param dataset: (*str*) The dataset object containing the target values.
    :param preds: (*numpy.ndarray*) Prediction results.
    :param font_size: (*int, optional*) The size of text in the generated figure (*default* = 16).
    :param min_val: (*float, optional*) The minimum value of the X and Y axes (*default* = ``None``).
    :param max_val: (*float, optional*) The maximum value of the X and Y axes (*default* = ``None``).
    """

    targets = dataset.y

    if min_val is None:
        min_val = numpy.minimum(numpy.min(targets), numpy.min(preds))
        min_val -= 0.2 * min_val

    if max_val is None:
        max_val = numpy.maximum(numpy.max(targets), numpy.max(preds))
        max_val += 0.2 * max_val

    plt.tight_layout()
    plt.rcParams.update({'font.size': font_size})
    plt.title('Scatter Plot of Prediction Results')
    plt.xlabel('Target value')
    plt.ylabel('Predicted value')
    plt.grid(linestyle='--')
    plt.xlim([min_val, max_val])
    plt.ylim([min_val, max_val])
    plt.plot([min_val, max_val], [min_val, max_val], 'k', zorder=2)
    plt.scatter(targets, preds, edgecolor='k', zorder=3)
    plt.savefig(fig_name, bbox_inches='tight', dpi=500)
    plt.close()


def plot_embeddings(fig_name: str,
                    data: numpy.ndarray,
                    labels: numpy.ndarray,
                    font_size: int = 16,
                    emb_method: str = EMB_TSNE):
    """
    Draw a scatter plot of the data embeddings from ``data`` and ``emb_method``.
    This function generates 2-dimensional scatter plot based on first and second components of the embedding method.
    Available embedding method are given in ``maica.core.env``.

    :param fig_name: (*str*) A name of the image file storing the scatter plot.
    :param data: (*numpy.ndarray*) The original data to be embedded.
    :param labels: (*labels*) Numerical labels for the data.
    :param font_size: (*int, optional*) The size of text in the generated figure (*default* = 16).
    :param emb_method: (*str, optional*) Embedding method (*default* = ``env.EMB_TSNE``).
    """

    if emb_method == EMB_TSNE:
        embs = TSNE(n_components=2).fit_transform(data)
    elif emb_method == EMB_SPECT:
        embs = SpectralEmbedding(n_components=2).fit_transform(data)

    plt.tight_layout()
    plt.rcParams.update({'font.size': font_size})
    plt.title('Scatter Plot of Data Embeddings')
    plt.xlabel('Latent Feature #1')
    plt.ylabel('Latent Feature #2')
    plt.scatter(embs[:, 0], embs[:, 1], edgecolor='k', c=labels, zorder=3)
    plt.colorbar()
    plt.savefig(fig_name, bbox_inches='tight', dpi=500)
    plt.close()
