#!/usr/bin/env python3

'''
Methods for visualizations of timeseries data based on the seaborn package.
'''

from pandas import Series
import seaborn as sns
import matplotlib.pyplot as plt

def sns_line_plot_series(series: Series, show=True) -> None:
  sns.lineplot(data=series)
  if show:
    plt.show()
  # TODO generate and return graphic
  return

def sns_line_plot_ci(series: Series, show=True) -> None:
  # TODO Area plot between ci_hi and ci_lo
  sns.lineplot(data=series)
  if show:
    plt.show()
  # TODO generate and return graphic
  return