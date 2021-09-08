#!/usr/bin/env python3

'''
Methods for univariate descriptive timeseries analysis.
'''

import pandas as pd
from pandas import Series, DataFrame
import math

def simple_descriptive_analysis(series: Series) -> dict:
  '''
    Returns dictionary with TimeSeries specific features.
    This method generates a simple descriptive analysis of the timeseris data.
    TODO ...
    @param series: pd.Series
     
  '''
  result = {
    'min': series.min(),
    'mean': series.mean(),
    'median': series.median(),
    'max': series.max(),
    'std': series.std(),
    'var': series.var(),
    'largest': series.nlargest(),
    'smallest': series.nsmallest()
  }
  return result

def rolling_mean(series: Series, window=5) -> Series:
  '''
    Returns a Series with the rolling mean.
    @param series: pd.Series
  '''
  return series.rolling(window, min_periods=1).mean()

def rolling_std(series: Series, window=5) -> Series:
  '''
    Returns a Series with the rolling std.
    @param series: pd.Series
  '''
  return series.rolling(window, min_periods=1).std()

def confidence_interval(series: Series) -> DataFrame:
  '''
    Returns a DataFrame with three columns, the upper and lower bound and the rolling mean for the confidence interval of the input timeseries.
    @param series: pd.Series
  '''
  result_df = pd.DataFrame()
  result_df['mean'] = rolling_mean(series)
  buf_std = rolling_std(series)
  ci95_hi = []
  ci95_lo = []
  for i in range(0,len(result_df.index)):
    ci95_hi.append(result_df['mean'][i] + 1.95*buf_std[i]/math.sqrt(5))
    ci95_lo.append(result_df['mean'][i] - 1.95*buf_std[i]/math.sqrt(5))
  
  result_df['ci_hi'] = ci95_hi
  result_df['ci_lo'] = ci95_lo
  return result_df

def value_distribution(series: Series, bins=-1) -> Series:
  '''
    Returns a DataFrame with the value distribution of the input timeseries (rounded).
    @param series: pd.Series
  '''
  if bins==-1:
    return series.round().value_counts().sort_index()
  else:
    return series.round().value_counts(bins=bins).sort_index()