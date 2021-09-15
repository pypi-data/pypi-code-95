from bertdotbill.defaults import default_terminal_address
from bertdotbill.defaults import terminal_check_timeout
from bertdotbill.logger import Logger
import socket
from bertdotconfig import Struct
from bertdotbill.config import SuperDuperConfig

logger = Logger().init_logger(__name__)

class Terminals():

  def __init__(self, **kwargs):
    self.settings = kwargs['settings']
    self.args = kwargs['args']
    self.superconf = SuperDuperConfig(verify_tls=self.args.verify_tls)
    self.default_console_address = self.superconf.get(
      self.settings,'terminals.default.address', 
      default_terminal_address
    )
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  def load(self, section):

    terminals = self.settings.get('terminals', {})
    
    if terminals:
      terminal_address = terminals.get(
        section,{}).get('address', self.default_console_address)
    else:
      terminal_address = self.default_console_address
    logger.info('Terminal address for section {s}: {a}'.format(
      s=section, a=terminal_address
    ))
    
    return terminal_address