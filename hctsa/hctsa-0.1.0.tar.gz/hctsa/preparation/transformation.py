#!/usr/bin/env python3

'''
Methods to transform univariate timeseries data, a restructuring of the data (e.g., calculate the differences between each point).
'''

from pandas import Series

def point_absdiff_transformation(series: Series) -> Series:
  '''
    Returns calculate the absolute differences between the points as a new transformation of the time series.
    First index of the original time series is lost, as the new one has one value less.
    @param series: pd.Series
  '''
  _values = []
  for i in range(1, len(series)):
    _values.append(abs(series[i] - series[i-1]))
  return Series(data=_values, index=series.index[1:])

def point_slope_transformation(series: Series) -> Series:
  '''
    Returns calculate the slope between the points as a new transformation of the time series.
    First index of the original time series is lost, as the new one has one value less.
    @param series: pd.Series
  '''
  _values = []
  print(series)
  for i in range(1, len(series)):
    _values.append(series[i] - series[i-1])
  return Series(data=_values, index=series.index[0:-1])

