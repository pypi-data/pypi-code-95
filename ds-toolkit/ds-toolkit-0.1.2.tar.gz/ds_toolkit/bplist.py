import plistlib
import json
from datetime import datetime

from ds_toolkit.files import write_to_file


def bplist_read_file(file_path):
    """
    Reads a bplist file.

    Args:
        file_path (sttr):

    Returns:
        dict:
    """
    with open(file_path, 'rb') as file:
        return plistlib.load(file)


def bplist_write_bplist_to_json(bplist_file_path, to_file_path):
    """
    Reads a bplist file and writes it to a json file.

    Args:
        bplist_file_path (str):
        to_file_path (str):
    """

    def _convert_datetime(o):
        if isinstance(o, datetime):
            return o.__str__()

    data = bplist_read_file(bplist_file_path)
    write_to_file(to_file_path, json.dumps(data, indent=2, default=_convert_datetime))
