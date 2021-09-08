#####################################################################
# Copyright (c) The Caleydo Team, http://caleydo.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#####################################################################


def phovea(registry):
  """
  register extension points
  :param registry:
  """
  # generator-phovea:begin

  registry.append('namespace', 'phovea_security_store_generated_api', 'phovea_security_store_generated.api', {
      'namespace': '/api/tdp/security_store_generated'
  })

  registry.append('user_stores', 'phovea_security_store_generated_store', 'phovea_security_store_generated.store', {})
  # generator-phovea:end
  pass


def phovea_config():
  """
  :return: file pointer to config file
  """
  from os import path
  here = path.abspath(path.dirname(__file__))
  config_file = path.join(here, 'config.json')
  return config_file if path.exists(config_file) else None
