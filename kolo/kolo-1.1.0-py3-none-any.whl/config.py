import logging
from pathlib import Path
from typing import Any, MutableMapping

import toml
from cerberus import Validator


logger = logging.getLogger("kolo")


schema = {
    "filters": {
        "type": "dict",
        "schema": {
            "include_frames": {"type": "list"},
            "ignore_frames": {"type": "list"},
            "ignore_request_paths": {"type": "list"},
        },
    }
}
validator = Validator(schema, allow_unknown=False)


def clear_errors(config: MutableMapping[str, Any], errors) -> None:
    for error in errors:
        key = error.document_path[-1]
        if error.info:
            for info in error.info:
                clear_errors(config[key], info)
        else:
            del config[key]


def load_config_from_toml(path: Path) -> MutableMapping[str, Any]:
    try:
        with open(path) as conf:
            config = toml.load(conf)
    except FileNotFoundError:
        return {}
    if not validator.validate(config):
        logger.warning("Kolo config file has errors: %s", validator.errors)
        clear_errors(config, validator._errors)
    return config
