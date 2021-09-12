from boost_hist_plot import plot_error_hist, plot_hist

import numpy as np
import matplotlib.pyplot as plt
# Python package providing Python bindings for the C++ Boost.Histogram
# https://boost-histogram.readthedocs.io/en/latest/
import boost_histogram as bh

# Generate a signal and a background distribution
rng = np.random.RandomState(0)
signal = rng.normal(loc=1, scale=0.1, size=(100, 1))
background = rng.normal(loc=0, scale=1, size=(100, 1))

# Fill Boost histograms
hist_params = {
    'bins': 50,
    'start': -5,
    'stop': 5,
    }

signal_hist = bh.Histogram(bh.axis.Regular(**hist_params),
                           storage=bh.storage.Weight())
signal_hist.fill(signal[:, 0])

background_hist = bh.Histogram(bh.axis.Regular(**hist_params),
                               storage=bh.storage.Weight())
background_hist.fill(background[:, 0])

# Plot errorbars
fig, ax = plt.subplots()
plot_error_hist(signal_hist, fmt='.', ax=ax)

# Plot stacked histogram
fig, ax = plt.subplots()
plot_hist([background_hist, signal_hist],
          ax=ax, stacked=True, histtype='stepfilled', edgecolor='black')

plt.show()
