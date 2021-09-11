import os

import tomli


def load_global_config(path=None):
    """This functions looks for a global config file"""
    home = os.path.expanduser("~")
    default_paths = [
        os.path.join(home, ".config", "labo", "labo.toml"),
        os.path.join(home, ".config", ".labo.toml"),
    ]

    if path:
        with open(path, "r") as f:
            conf = tomli.load(f)
            return conf
    else:
        for p in default_paths:
            if os.path.isfile(p):
                with open(p, "r") as f:
                    conf = tomli.load(f)
                    return conf

    return None
