#!/usr/bin/env python3

'''
Methods for normalization of timeseries data.
'''

from pandas import DataFrame, Series

def standard(df: DataFrame) -> DataFrame:
  '''
    Returns standard normalization of the TimeSeries data.
    @param df: pd.DataFrame
  '''
  if isinstance(df, DataFrame):
    for col in list(df.columns):
      df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
  elif isinstance(df, Series):
    df = df.apply(lambda x: ((x - df.min()) / df.max() - df.min()))
  else:
    ... # TODO error wrong type
  return df
  
def zscore(df: DataFrame) -> DataFrame:
  '''
    Returns zscore normalization of the TimeSeries data.
    @param df: pd.DataFramee
  '''
  if isinstance(df, DataFrame):
    for col in list(df.columns):
      df[col] = (df[col] - df[col].mean()) / df[col].std(ddof=0)
  elif isinstance(df, Series):
    df = df.apply(lambda x: ((x - df.mean()) / df.std(ddof=0)))
  else:
    ... # TODO error wrong type
  return df