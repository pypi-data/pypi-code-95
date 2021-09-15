import configparser
import os

def readConfig(configFile = os.path.dirname(__file__) + "/" + "wdltest.cfg"):
  config = configparser.ConfigParser()
  config.read(configFile)
  return config
