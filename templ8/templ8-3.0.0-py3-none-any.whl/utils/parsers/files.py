import json
from typing import Any, Dict

import yaml

from ...utils.parsers.exceptions import FileParsingError, UnsupportedFormat
from ...utils.strings.paths import path_ext


def parse_yaml(path: str) -> Dict[str, Any]:
    if path_ext(path) not in [".yml", ".yaml"]:
        raise UnsupportedFormat(path, "YAML")

    with open(path, "r", encoding="utf8") as stream:
        try:
            return yaml.safe_load(stream)

        except yaml.scanner.ScannerError as err:
            raise FileParsingError(path) from err


def parse_json(path: str) -> Dict[str, Any]:
    if path_ext(path) != ".json":
        raise UnsupportedFormat(path, "JSON")

    with open(path, "r", encoding="utf8") as stream:
        try:
            return json.load(stream)

        except json.decoder.JSONDecodeError as err:
            raise FileParsingError(path) from err
