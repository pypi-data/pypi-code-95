# -*- coding: utf8 -*-

import json
import math
import os
import shutil
from enum import IntEnum
from os import path

from xlang import logger


class SizeType(IntEnum):
    BYTE = 0
    KB = 1
    MB = 2
    GB = 3
    TB = 4
    PB = 5
    EB = 6
    ZB = 7
    YB = 8
    DB = 9
    NB = 10

    def radix(self) -> float:
        return math.pow(1024, self.value)


def get_file_size(filepath, stype: SizeType = SizeType.KB):
    return path.getsize(filepath) / stype.radix()


def get_file_name(abspath: str) -> str:
    return path.splitext(path.basename(abspath))[0]


def get_file_suffix(abspath: str) -> str:
    return path.splitext(path.basename(abspath))[1]


def split_path(abspath: str):
    dir_path, f_name, suffix = '', '', ''
    if abspath:
        dir_path = path.dirname(abspath)
        base_name = path.basename(abspath)
        split_array = path.splitext(base_name)
        f_name = split_array[0]
        suffix = split_array[1]

    return dir_path, f_name, suffix


def remove_sub_files(del_path):
    if path.exists(del_path):
        for file in os.listdir(del_path):
            file_path = path.join(del_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif path.isdir(file_path):
                shutil.rmtree(file_path)


def dumps(data_json: dict):
    return json.dumps(data_json, sort_keys=True, indent=4, ensure_ascii=False)


def write_json(outfile, json_dict: dict):
    result = False

    if json_dict and len(json_dict):
        backup_file = outfile + '.backup'

        father_path = path.abspath(path.join(path.dirname(outfile), path.curdir))
        os.makedirs(father_path, exist_ok=True)

        try:
            if path.exists(outfile) and path.getsize(outfile):
                shutil.copy(outfile, backup_file)

            with open(outfile, 'w+') as out:
                json.dump(json_dict, out)

            result = path.exists(outfile) and path.getsize(outfile)
        except Exception as e:
            logger.exception(e)

            shutil.copy(backup_file, outfile)

    return result
