#!/usr/bin/env python3

'''
Methods to prepare multivariat timeseries data for multivariat methods/combinations.
'''

# TODO
# Vorbereitung der Zeitreihen zur weiteren Verarbeitung (auf gleiche länge schneiden z.B.)
# Kombinationen von Zeitreihen ('ueberlagerung')

from pandas import Series

def merge_sum(series: Series, add_series: Series) -> Series:
  '''
    Returns a merge Series, representing the sum of the values per index of both Series (series + add_series).
    @param series: pd.Series
  '''
  return series + add_series

def merge_subtract(series: Series, add_series: Series) -> Series:
  '''
    Returns a merge Series, representing the subtract of the values per index of both Series (series - add_series).
    @param series: pd.Series
  '''
  return series - add_series

def merge_multiply(series: Series, add_series: Series) -> Series:
  '''
    Returns a merge Series, representing the product of the values per index of both Series (series * add_series).
    @param series: pd.Series
  '''
  return series * add_series

def merge_divide(series: Series, add_series: Series) -> Series:
  '''
    Returns a merge Series, representing the division of the values per index of both Series (series / add_series).
    @param series: pd.Series
  '''
  return series / add_series

def merge_mean(series: Series, add_series: Series) -> Series:
  '''
    Returns a merge Series, representing the mean of the values per index of both Series((series + add_series) / 2).
    @param series: pd.Series
  '''
  return (series + add_series) / 2