import os
import shutil

def get_config_template(config_file):
    root = os.path.dirname(__file__)
    cwd = os.getcwd()
    shutil.copy(os.path.join(root, config_file), cwd)