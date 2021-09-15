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
    import sysconfig
    root_package_name = __name__.split('.')[0]
    site_packages_path = sysconfig.get_paths()['purelib']
    site_scripts_path = sysconfig.get_paths()['scripts']
    root_package_path = os.path.join(site_packages_path, root_package_name)
    if os.path.isdir(root_package_path):
      logger.debug('Detected installation type is "pip"')
      html_index_file_path_relative = './%s/index.html' % gui_dirname
      html_index_file_path = os.path.join(site_scripts_path, gui_dirname, 'index.html')
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