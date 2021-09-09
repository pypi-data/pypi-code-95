from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import copy
import os
import json
import logging
from datetime import datetime
from infiniguard_health.blueprints.components import SystemState

JSON_FILE_NAME = '/run/latest_system_health_state.json'
LOCKED_JSON_FILE_NAME = JSON_FILE_NAME + '.locked'
DATA_HAS_EXPIRED_SECONDS = 3 * 60

_logger = logging.getLogger(__name__)


def _convert_keys_to_int(json_sub_dict):
    component_with_int_keys = {}

    for key, value in json_sub_dict.items():
        if isinstance(key, str) and key.isdigit():
            new_key = int(key)
        else:
            new_key = key

        component_with_int_keys[new_key] = copy.deepcopy(json_sub_dict[key])

    return component_with_int_keys


def write_system_state_to_file(system_state):
    """
    Receives a SystemState object.
    Serializes the object and saves it to a file on the disk, named 'latest_system_state.json'.
    The system state is saved into a new file, named 'latest_system_state.json.locked'.
    Once the file is done being written, the old 'latest_system_state.json' is deleted, and the new file has the
    '.locked' removed from it.
    This ensures that there is only one correct 'latest_system_state.json' available at any point in time.
    There is a short period, between deleting the last file and renaming the new one, in which there is only a locked
    file. In this case, the reader must wait until the unlocked file is available.

    Before starting the write process, the function adds to the SystemState object a new field "last_written_to_file",
    which holds the timestamp.
    """
    _logger.info(f"Writing system state into locked file {LOCKED_JSON_FILE_NAME}")
    system_state_dict = system_state.to_primitive()

    if os.path.exists(LOCKED_JSON_FILE_NAME):
        _logger.error(f"Locked file {LOCKED_JSON_FILE_NAME} exists. Wasn't cleaned up after previous read")
        os.remove(LOCKED_JSON_FILE_NAME)

    with open(LOCKED_JSON_FILE_NAME, 'x') as locked_json_file:
        json.dump(system_state_dict, locked_json_file)

    _logger.info(f"Finished writing system state into locked file.")

    if os.path.exists(JSON_FILE_NAME):
        _logger.info(f"Deleting old file {JSON_FILE_NAME}")
        os.remove(JSON_FILE_NAME)

    _logger.info(f"Renaming new locked file to {JSON_FILE_NAME}")
    os.rename(LOCKED_JSON_FILE_NAME, JSON_FILE_NAME)


@retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry=retry_if_exception_type(FileNotFoundError))
def read_system_state_from_file_as_dict(path=JSON_FILE_NAME):
    """
    Reads the system state from the JSON file.
    The write function renames the file to be 'latest_system_state.json' when the writing is finished (and before that
    has the suffix ".locked". If the complete file doesn't exist, the function waits until it does, timing out after
    a given amount.
    """
    with open(path, 'r') as json_file:
        # JSON saves all keys as strings. Since we use some of them as ints, we need to convert them back.
        json_data = json.load(json_file, object_hook=_convert_keys_to_int)
    return json_data


def read_system_state_from_file_as_native_object(path=JSON_FILE_NAME):
    _logger.info(f"Reading system state from file {path}")
    return SystemState(read_system_state_from_file_as_dict(path))


def is_latest_system_health_state_stale():
    return (datetime.now() - datetime.fromtimestamp(os.path.getmtime(JSON_FILE_NAME))).seconds > DATA_HAS_EXPIRED_SECONDS
