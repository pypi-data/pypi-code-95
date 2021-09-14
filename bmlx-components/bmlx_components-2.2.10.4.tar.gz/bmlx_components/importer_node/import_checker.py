import logging
import os
from typing import Text, List
from bmlx.utils import io_utils


def check_nothing(uri: Text):
    return True


def check_uri_exist(uri: Text):
    fs, path = io_utils.resolve_filesystem_and_path(uri)
    if not fs.exists(path):
        logging.warning("uri %s does not exist!", uri)
        return False
    return True


def check_succ_flag(uri: Text):
    fs, path = io_utils.resolve_filesystem_and_path(uri)
    if not fs.exists(path):
        logging.warning("uri %s does not exist!", uri)
        return False
    succ_flag_path = os.path.join(path, "_SUCCESS")
    if not fs.exists(succ_flag_path):
        logging.warning("succ flag uri %s does not exist!", succ_flag_path)
        return False
    return True


def check_skip_flag(uri: Text):
    fs, path = io_utils.resolve_filesystem_and_path(uri)
    if not fs.exists(path):
        logging.warning("uri %s does not exist!", uri)
        return False
    skip_flag_path = os.path.join(path, "_DIRTY")
    if fs.exists(skip_flag_path):
        logging.warning("skip flag uri %s exist!", skip_flag_path)
        return True
    return False


def check_uri_and_files_exist(uri: Text, files: List[Text] = []):
    fs, path = io_utils.resolve_filesystem_and_path(uri)
    if not fs.exists(path):
        logging.warning("uri %s does not exist!", uri)
        return False
    for file in files:
        if not fs.exists(os.path.join(uri, file)):
            logging.warning("file %s in uri %s does not exist!", file, uri)
            return False
    return True
