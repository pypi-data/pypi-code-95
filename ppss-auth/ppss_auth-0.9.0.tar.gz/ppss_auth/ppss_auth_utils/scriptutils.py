from sys import argv
import os
import configparser
from sqlalchemy import engine_from_config
from pyramid.paster import (
  setup_logging,
)

def configFromArgv():
  config_uri = argv[-1]
  setup_logging(config_uri)  
  config = configparser.ConfigParser() 
  with open(config_uri,"r") as inifile:
    config.read_string(inifile.read())
  
  here = os.getcwd()
  config["app:main"]["here"] = here
  return config

def engineFromConfig(config):
  engine = engine_from_config(config["app:main"], "sqlalchemy.")
  return engine