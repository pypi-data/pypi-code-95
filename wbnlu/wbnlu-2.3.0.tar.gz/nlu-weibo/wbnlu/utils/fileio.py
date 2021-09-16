import yaml
from typing import Text
from wbnlu import logger


logger = logger.my_logger(__name__)


def read_yaml_file(filename: Text, encoding: Text = 'utf-8'):
    with open(filename) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

