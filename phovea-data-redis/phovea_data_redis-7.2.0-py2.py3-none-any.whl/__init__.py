###############################################################################
# Caleydo - Visualization for Molecular Biology - http://caleydo.org
# Copyright (c) The Caleydo Team. All rights reserved.
# Licensed under the new BSD license, available at http://caleydo.org/license
###############################################################################


def phovea(registry):
  """
  register extension points
  :param registry:
  """
  registry.append('manager', 'idmanager', 'phovea_data_redis.assigner', dict(priority=-5, singleton=True))
  registry.append('mapping_provider', 'phovea_data_redis', 'phovea_data_redis.mapping_table')
  registry.append('manager', 'cachemanager', 'phovea_data_redis.cache', dict(priority=-5, singleton=True))
  registry.append('json-encoder', 'bytes-to-string-encoder', 'phovea_data_redis.bytes_to_string_encoder', {})
  pass


def phovea_config():
  """
  :return: file pointer to config file
  """
  from os import path
  here = path.abspath(path.dirname(__file__))
  config_file = path.join(here, 'config.json')
  return config_file if path.exists(config_file) else None
