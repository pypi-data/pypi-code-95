#!/usr/bin/env python3

'''
Methods for multivariate descriptive timeseries analysis.
'''

# TODO
# correlation
# Series.corr(other, method='pearson', min_periods=None)
# covarianz

from pandas import Series

def corr(series: Series, add_series: Series, method='pearson') -> int:
  '''
    Returns the correlation between both timeseries, based on method (pearson, kendall, spearman).
    @param series: pd.Series
    @param add_series: pd.Series
    @param method: str
  '''
  return series.corr(add_series, method=method)