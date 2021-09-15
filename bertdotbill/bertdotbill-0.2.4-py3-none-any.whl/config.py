from bertdotbill.auth import get_credential
from bertdotbill.defaults import settings as default_settings
from bertdotbill.logger import Logger
import os
from bertdotconfig import SuperDuperConfig

logger = Logger().init_logger(__name__)

def read_config(**kwargs):

  args = kwargs['args']
  verify_tls = kwargs.get('verify_tls', False)

  try:
    script_dir = os.path.dirname(os.path.abspath(my.invocation.path))
  except NameError:
    script_dir = os.path.dirname(os.path.abspath(__file__))
  if not args.config_file:
    logger.debug('No config file specified')
  default_config_file_name = 'bill.config.yaml'
  default_config_file_search_paths = [
  os.path.abspath(os.path.join(script_dir)),
  "~/.bill"
  ]
  config_file_path = args.config_file
  # Initialize Config Module
  superconf = SuperDuperConfig(
    extra_config_search_paths=default_config_file_search_paths,
    verify_tls=verify_tls
  )
  # Initialize App Config
  initial_data = {
  'environment': os.environ,
  'get_credential': get_credential
  }  
  settings = superconf.load_config(
    config_file_name=default_config_file_name,
    templatized=args.config_file_templatized,
    initial_data=initial_data
  )
  if not settings:
    settings = default_settings  
  external_configs = settings.get('external_configs', [])
  for external_config in external_configs:
    if isinstance(external_config, dict):
      config_uri = external_config.get('uri')
      if config_uri:
        config_uri_username = external_config.get('auth',{}).get('username')
        config_uri_password = external_config.get('auth',{}).get('password')
        external_settings = superconf.load_config(
          config_file_uri=config_uri,
          auth_username=config_uri_username,
          auth_password=config_uri_password,
          templatized=args.config_file_templatized,
          initial_data=initial_data
        )
        if external_settings:
          settings = superconf.Merge(settings, external_settings)
  return superconf, settings