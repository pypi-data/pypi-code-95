import json
import os
import sys
from shutil import copyfile


def load_conf(path):
    try:
        with open(os.path.join(path, "config.json"), "r") as confile:
            return json.load(confile)
    except Exception as e:
        print('ERROR - Could not open config.json: %s %s' % (type(e), e))
        sys.exit(1)


def create_conf_example(dir_path):
    file_path = os.path.join(dir_path, "config.json")
    if not os.path.isfile(file_path):
        copyfile(os.path.join(os.path.dirname(__file__), "config.json.example"), file_path)
    else:
        print('WARNING - The config.json file already exists in %s' % os.path.realpath(dir_path))


def check_config():
    """
    Check if config file has required format
    """
    return
