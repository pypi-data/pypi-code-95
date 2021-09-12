import os
import yaml

from pathlib import Path

import cnvrg.helpers.env_helper as env_helper

CONFIG_TYPE_PROJECT = "PROJECT"
CONFIG_TYPE_DATASET = "DATASET"

def find_config_dir(path=None):
    currdir = path or os.curdir
    real_path = os.path.realpath(currdir)
    home_path = os.path.expanduser("~")
    while real_path != home_path and real_path != Path(home_path).anchor and real_path != ".":
        if os.path.exists(os.path.join(currdir, '.cnvrg', 'config.yml')):
            return currdir
        tmp_path = Path(real_path)
        currdir = tmp_path.parent
        real_path = os.path.realpath(currdir)
    return False


def config_path(path=None):
    config_dir = find_config_dir(path=path)
    if not config_dir: return
    return os.path.join(config_dir, ".cnvrg", "config.yml")


def load_config(path=None):
    if not path: return {}
    with open(config_path(path), 'r') as f:
        return yaml.safe_load(f)


def config_type(path=None):
    if not find_config_dir(path):
        return None
    config = load_config(path=path)
    if "project" in config or ":project_name" in config:
        return CONFIG_TYPE_PROJECT
    return CONFIG_TYPE_DATASET


def save_config(config, path=None):
    config_dir = find_config_dir(path=path)
    config_dir = os.path.join(config_dir or path, ".cnvrg")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.yml")
    with open(config_path, "w+") as f:
        yaml.dump(config, f)

def idx_path(path=None):
    config_dir = find_config_dir(path=path)
    if not config_dir: return
    return os.path.join(config_dir, ".cnvrg", "idx.yml")

def load_idx(path=None):
    if not path: return {}

    with open(idx_path(path), 'r') as f:
        return yaml.safe_load(f)

def is_in_dir(dir_type, dir_element, working_dir):
    working_dir = working_dir or os.curdir
    if not find_config_dir(working_dir): return False
    if not config_type(working_dir) == dir_type: return False
    config = load_config(working_dir)
    return (config.get(":project_slug") or config.get("project") or config.get(":dataset_slug") or config.get("dataset_name") or config.get("dataset")) == dir_element


def get_element_slug(working_dir=None):
    config = load_config(find_config_dir(working_dir))
    return env_helper.CURRENT_PROJECT_SLUG or config.get(":project_slug") or config.get("project_slug") or config.get("project") or config.get(":dataset_slug") or config.get("dataset_slug") or config.get("dataset")


def get_element_owner(working_dir=None):
    config = load_config(find_config_dir(working_dir))
    return env_helper.CURRENT_ORGANIZATION_SLUG or config.get(":owner") or config.get("owner")

def general_config_path():
    return os.path.expanduser("~/.cnvrg/config.yml")

def load_generl_config():
    config_file = general_config_path()
    if not os.path.isfile(config_file):
        return ""
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)
