#!/usr/bin/env python3

'''
Method mapping file, needed for the string to method mapping functionality.
'''

# Imports
from ..preparation.normalization import *
from ..preparation.transformation import *
from ..preparation.multivariat import *
from ..descriptive.univariate import *
from ..descriptive.multivariat import *
from ..visualization.seaborn import *

# Preparations.Normalizations
def prep_norm_zscore(df: DataFrame) -> DataFrame:
  return zscore(df)

def prep_norm_standard(df: DataFrame) -> DataFrame:
  return standard(df)

# Preparation.Multivariat
def prep_merge_sum(series: Series) -> Series:
  return merge_sum(series)

def prep_merge_subtract(series: Series) -> Series:
  return merge_subtract(series)

def prep_merge_multiply(series: Series) -> Series:
  return merge_multiply(series)

def prep_merge_divide(series: Series) -> Series:
  return merge_divide(series)

def prep_merge_mean(series: Series) -> Series:
  return merge_mean(series)

# Preparations.Transformation
def prep_transform_point_absdiff_transformation(series: Series) -> Series:
  return point_absdiff_transformation(series)

def prep_transform_point_slope_transformation(series: Series) -> Series:
  return point_slope_transformation(series)

# Descriptive.Univariate
def descr_uni_rolling_mean(series: Series) -> Series:
  return rolling_mean(series)

def descr_uni_rolling_std(series: Series) -> Series:
  return rolling_std(series)

def descr_uni_confidence_interval(series: Series) -> DataFrame:
  return confidence_interval(series)

def descr_uni_value_distribution(series: Series) -> Series:
  return value_distribution(series)

def descr_uni_simple_descriptive_analysis(series: Series) -> dict:
  return simple_descriptive_analysis(series)

# Descriptive.Multivariat
def descr_corr(series: Series, add_series: Series) -> int:
  return corr(series, add_series)

# Visualizations.Seaborn
def viz_sns_line_plot_series(series: Series) -> None:
  # TODO return graphic.. 
  return sns_line_plot_series(series)

def viz_sns_line_plot_ci(series: Series) -> None:
  # TODO return graphic.. 
  return sns_line_plot_ci(series)