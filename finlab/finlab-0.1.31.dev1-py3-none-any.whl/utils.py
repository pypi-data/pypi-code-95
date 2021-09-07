import os
import logging
import requests
from finlab import get_token

# Get an instance of a logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def raise_permission_error(*args, **kwargs):
    raise Exception("Only VIP users can access backtest.sim function")  

def auth_permission(allow_roles=None):
  def decorator(func):
    def warp(*args, **kwargs):
      if allow_roles is None:
        return func(*args, **kwargs)
      role = os.environ.get('finlab_role')
      if role in allow_roles:
        return func(*args, **kwargs)
      else:
          logger.error(f"Your role is {role} that don't have permission to use this function.")
    return warp
  return decorator

def download_encrypted_py_file(folder, module_name):
    api_token = get_token()
    
    pye_file_name = f'{folder}__{module_name}.pye'
    encrypted_folder = 'encrypted_py_files'

    request_args = {
        'api_token': api_token,
        'bucket_name':'finlab_tw_stock_item',
        'blob_name': os.path.join(encrypted_folder, pye_file_name)
    }

    url = 'https://asia-east2-fdata-299302.cloudfunctions.net/auth_generate_data_url'
    auth_url = requests.get(url, request_args)
    
    from sourcedefender.tools import getUrl
    getUrl(auth_url.text)
    