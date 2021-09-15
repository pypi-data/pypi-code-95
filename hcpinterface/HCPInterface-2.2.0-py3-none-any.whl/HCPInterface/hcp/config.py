import os

from configparser import ConfigParser
from HCPInterface import WD

def get_config():
    config = ConfigParser()
    config_path = os.path.join(WD, '..', 'config.ini')
    config.read(config_path)

    return config
