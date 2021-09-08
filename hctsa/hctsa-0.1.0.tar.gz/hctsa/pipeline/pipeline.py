#!/usr/bin/env python3

'''
Pipeline Class, for building a user defined pipeline for timeseries manipulation and analysis.
'''


import pkg_resources
import yaml
import pandas as pd

import hctsa.pipeline.methods as methods

class Pipeline():
  # Main Pipeline Array
  main_pipeline = []
  merge_pipeline = []

  # Main Data Variable
  core_data = []

  # List of additional Data
  add_data = []

  # DICTIONARIE for specific pipeline rules, loaded from method_rules.yml file.
  method_rules = []

  method_rules_source = pkg_resources.resource_filename(__name__, './method_rules.yml')
  
  def __init__(self, series: pd.Series = None) -> None:
    '''
      Initialization of a new Pipeline Object.
      @param series: pd.Series
    '''
    if series is not None:
      self.core_data = series
    # TODO add try/catch block
    #with open('./pipeline/method_rules.yml', 'r') as file:
    with open(self.method_rules_source, 'r') as file:
      self.method_rules = yaml.safe_load(file)
    return

  def load_data_csv(self, filename: str) -> None:
    '''
      Loads pd.Series data as core_data from filename.
      @param filename: str
    '''
    if filename == 'test':
      self.core_data = pd.read_csv('../test_data/testdata.csv', squeeze=True)
    else:
      self.core_data = pd.read_csv(filename, squeeze=True)
    return filename + ' loaded'

  def add_method(self, add_function: str, position: int = -1) -> bool:
    '''
      Adds a new method into the pipeline
      1) Check actual pipeline
      2) Check if method can be added at defined position or at the end (-1), regarding to the pipeline-rules (e.g. visualisation is the last layer/method)
        -> check if method is in method_rules.yml for specific "nachfolger function"
      3) if possible, add method to method-pipeline-array
      Return boolean - success or error msg
      @param add_function: str
      @param position: int
    '''
    if(len(self.main_pipeline)) > 0:
      last_func = self.main_pipeline[-1]
      if(add_function in self.method_rules['methods'][last_func]):
        self.main_pipeline.append(add_function)
      else:
        print('error: function cannot be added: ', add_function)
        return False
    else:
      if(add_function in self.method_rules['start']):
        self.main_pipeline.append(add_function)
      else:
        print('error: function cannot be added: ', add_function)
        return False
    return True

  def del_method(self, position = -1) -> bool:
    self.main_pipeline.pop(position)
    return True

  def reset_pipeline(self) -> None:
    '''
      Resetting the main_pipeline and core_data to an empty array [].
    '''
    self.main_pipeline = []
    self.core_data = []
    return True

  def add_series(self, series: pd.Series, merge_method: str) -> bool:
    '''
      Add an additional timeseries into the pipeline with a specific method for merging two timeseries data (e.g. calculate the correlation)
    '''
    if self.add_method(merge_method):
      self.add_data.append(series)
    return True

  def run(self) -> pd.Series:
    '''
      Returns the result of the Pipeline.
      Method for running the pipeline. Every method that was added into the pipeline will get executed in a sequential way.
      TODO if _data is empty -> error
    '''
    _data = self.core_data
    print('PIPELINE: ', self.main_pipeline)
    for method in self.main_pipeline:
      print('DOING: ', method)
      if method in self.method_rules['merge_methods']:
        _data = getattr(methods, method)(_data, self.add_data[0])
        del self.add_data[0]
      else:
        _data = getattr(methods, method)(_data)
      print(_data)
    return _data