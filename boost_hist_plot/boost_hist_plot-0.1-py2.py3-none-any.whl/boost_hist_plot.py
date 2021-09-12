''' Functions to plot boost histograms.'''
__version__ = '0.1'

import numpy as np


def plot_error_hist(hist, ax, **kwargs):
    ''' Errorbar plot from boost histogram.

    Parameters
    ----------
    hist : boost_histogram.Histogram
        Histogram to plot.
    ax : matplotlib.axes.Axes
        Axes instance for plotting.
    **kwargs
        Keyword arguments forwarded to ax.errorbar().

    Returns
    -------
    None
    '''
    errorbar_params = {
        'x': hist.axes[0].centers,
        'y': hist.view().value,
        'yerr': kwargs.get('yerr', np.sqrt(hist.view().variance)),
        }
    ax.errorbar(**errorbar_params, **kwargs)


def plot_hist(hist, ax, poisson_uncertainty=True, **kwargs):
    ''' Histogram plot from boost histogram.

    Parameters
    ----------
    hist : boost_histogram.Histogram
        Histogram to plot.
    ax : matplotlib.axes.Axes
        Axes instance for plotting.
    poisson_uncertainty : bool
        If True, plot the Poisson uncertainty.
    **kwargs
        Keyword arguments forwarded to ax.hist().

    Returns
    -------
    None
    '''
    if not isinstance(hist, list):
        # if single hist, create a list with a single element
        hist = [hist]
    bins = hist[0].axes[0].edges
    # Data sample made of the bin centers of the input histograms
    x = [h.axes[0].centers for h in hist]
    # Each "data point" is weighed according to the bin content
    weights = [h.view().value for h in hist]
    if poisson_uncertainty:
        plot_error_hist(sum(hist), fmt=' ', ax=ax, color='k')
    ax.hist(x=x, bins=bins, weights=weights, **kwargs)
