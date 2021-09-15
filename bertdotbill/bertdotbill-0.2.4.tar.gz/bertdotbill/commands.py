from bertdotbill.logger import Logger
import os
import sys

logger = Logger().init_logger(__name__)

def run_command(command, args=None):
  logger.debug('Running command %s' % command)
  os.system(command)

def launch(settings, command_key, args=None):
    logger.info("Launching command mapped to '%s'" % command_key)
    commands = settings.get('commands',{})
    if commands.get(sys.platform,{}).get(command_key):
      command = commands.get(sys.platform,{}).get(command_key,{}).get('cmd')
    else:
      command = commands.get(command_key,{}).get('cmd')
    if command:
      run_command(command, args)
    else:
      logger.warning('No command key found for %s' % command_key)