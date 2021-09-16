from bertdotbill.logger import Logger
from bertdotbill.defaults import gui_dirname
import os
import sys

logger = Logger().init_logger(__name__)
is_frozen = getattr(sys, 'frozen', False)
if is_frozen:
  my_file_name = os.path.basename(sys.executable)
  project_root = os.path.dirname(os.path.abspath(sys.executable))  
else:
  my_file_name = __file__
  project_root = os.path.dirname(my_file_name)

def get_entrypoint():
  index_file_path_found = False
  logger.info('Determining path to index.html')
  if is_frozen: # Check for frozen pyinstaller app
    logger.debug('Detected installation type is "frozen"')
    html_index_file_path_relative = './%s/index.html' % gui_dirname
    html_index_file_path = os.path.join(project_root, html_index_file_path_relative)
    logger.info('Checking %s' % html_index_file_path)
    if os.path.exists(html_index_file_path):
      index_file_path_found = True
      logger.info('Found %s' % html_index_file_path)
      return html_index_file_path
    else: # Check for frozen py2app
      html_index_file_path_relative = '../Resources/%s/index.html' % gui_dirname
      html_index_file_path = os.path.join(project_root, html_index_file_path_relative)
      logger.info('Checking %s' % html_index_file_path)
      if os.path.exists(html_index_file_path):
        index_file_path_found = True
        logger.info('Found %s' % html_index_file_path)
        return html_index_file_path_relative
      else:
        logger.error('%s not found' % html_index_file_path)
  else: # Check for unfrozen development app
    import re
    import site
    import sysconfig
    root_package_name = __name__.split('.')[0]
    site_packages_path = sysconfig.get_paths()['purelib']
    user_scripts_paths = [p for p in site.getsitepackages() if 'site-packages' in p]
    if len(user_scripts_paths) > 0:
      user_scripts_path = user_scripts_paths[0]
      user_package_path = os.path.realpath(os.path.join(user_scripts_path, root_package_name))
    else:
      user_scripts_path, user_package_path = 'DNE'
    root_package_path = os.path.realpath(os.path.join(site_packages_path, root_package_name))
    try:
      import bertdotbill
      pip_package_path = ''.join(bertdotbill.__path__)
      if 'site-packages' in pip_package_path:
        logger.debug('Found pip package path at %s' % pip_package_path)
        if sys.platform == 'win32':
          package_path = root_package_path if os.path.isdir(root_package_path) else user_package_path
        else:
          pattern = re.compile('/lib/.*')
          logger.debug('Platform is POSIX-compliant')
          package_path_base_dir = pattern.sub('', ''.join(pip_package_path))
          package_path = os.path.join(package_path_base_dir, 'bin')
          logger.debug('Using pip package path of %s' % package_path)
      else:
        package_path = 'DNE'
        logger.debug('pip package does not exist')
    except Exception:
      pass
    if os.path.isdir(package_path):
      logger.debug('Detected installation type is "pip"')
      html_index_file_path_relative = './%s/index.html' % gui_dirname
      html_index_file_path = os.path.join(package_path, gui_dirname, 'index.html')
    else:
      logger.debug('Detected installation type is "development"')
      html_index_file_path_relative = '../%s/index.html' % gui_dirname
      html_index_file_path = os.path.join(project_root, html_index_file_path_relative)
    logger.info('Checking %s' % html_index_file_path)
    if os.path.exists(html_index_file_path):
      index_file_path_found = True
      logger.info('Found %s' % html_index_file_path)
      return html_index_file_path_relative
    else:
      logger.error('%s not found' % html_index_file_path)
  if not index_file_path_found:
    raise Exception('No index.html found')