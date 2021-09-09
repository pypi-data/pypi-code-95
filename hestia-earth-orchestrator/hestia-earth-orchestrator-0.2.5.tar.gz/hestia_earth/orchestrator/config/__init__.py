import os
import sys
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)


def _load_config(config: str):
    path = os.path.join(CURRENT_DIR, config)
    if not os.path.exists(path):
        raise Exception(f"Configuration not found: {config} in {CURRENT_DIR}")
    with open(path) as f:
        return json.load(f)
