""" converts yml to json"""

import pathlib
import json
import yaml

from qary import constants

YAML_FILEPATH = pathlib.Path(constants.DATA_DIR, 'testsets', 'dialog', 'qa-2020-04-25.yml')
JSON_FILEPATH = pathlib.Path(constants.DATA_DIR, 'testsets', 'dialog', 'qa-2020-04-25.json')

def yaml_to_json(YAML_FILEPATH=YAML_FILEPATH, JSON_FILEPATH=JSON_FILEPATH):
    """converts yaml to json file

    >>> yaml_to_json(YAML_FILEPATH=YAML_FILEPATH, JSON_FILEPATH=JSON_FILEPATH)
    """

    with open(YAML_FILEPATH) as yml:
        data = yaml.load(yml)

    with open(JSON_FILEPATH, 'w') as js:
        json.dump(data, js, ensure_ascii=False, indent=2)

