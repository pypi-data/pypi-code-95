# Copyright Okera Inc.
#
#
#
# pylint: disable=wrong-import-order
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

try:
  import numpy
  HAS_NUMPY = True
except ImportError:
  HAS_NUMPY = False

try:
  import pandas
  HAS_PANDAS = True
except ImportError:
  HAS_PANDAS = False

NO_PANDAS_RUNTIME_ERROR = "The pandas library is required to perform scan operations."
NO_NUMPY_RUNTIME_ERROR = "The numpy library is required to perform scan operations."

def assert_numpy_installed():
  if not HAS_NUMPY:
    raise RuntimeError(NO_NUMPY_RUNTIME_ERROR)

def assert_pandas_installed():
  if not HAS_PANDAS:
    raise RuntimeError(NO_PANDAS_RUNTIME_ERROR)

def should_patch_botocore():
  import os
  if os.environ.get('OKERA_PATCH_BOTO', None):
    return True
  return False

def check_and_patch_botocore():
  if should_patch_botocore():
    from okera.botocore_patch import patch_botocore
    patch_botocore()

# Import the public API
from okera.odas import context, version
_default_app_context = context()

def initialize_default_context():
  import os
  host = os.environ.get('OKERA_PLANNER_HOST', None)
  if host:
    port = int(os.environ.get('OKERA_PLANNER_PORT', 12050))
    token = os.environ.get('OKERA_USER_TOKEN', None)
    if token:
      _default_app_context.enable_token_auth(token_str=token)
    return _default_app_context.connect(host=host, port=port)

_default_context = None
def get_default_context():
  global _default_context
  if not _default_context:
    _default_context = initialize_default_context()
  return _default_context

# Initialize boto3 patches if necessary
check_and_patch_botocore()

