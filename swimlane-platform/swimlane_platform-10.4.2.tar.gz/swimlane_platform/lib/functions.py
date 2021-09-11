import shutil
from os import path
import copy
from typing import Callable, Any, Dict


def apply_for_all_dict_values(dictionary, valid, func):
    # type: (Dict, Callable[[Any], bool], Callable[[Any], Any]) -> None
    """Applies func to all values in Dictionary that match valid function.
    :param dictionary: The dictionary to iterate
    :param valid: Function that validates type or other condition for value.
    :param func: Function to apply to the value and replace it.
    """

    def _iterate(value):
        """Inner function with wider object definition then parent.
        Created to keep parent strict signature."""
        if isinstance(value, dict):
            for _, _value in value.items():
                _iterate(_value)
        elif isinstance(value, list):
            for _value in value:
                _iterate(_value)
        if valid(value):
            func(value)

    _iterate(dictionary)


def merge_dictionaries(first_dictionary, second_dictionary, overwrite=False):
    # type: (dict, dict, bool) -> dict
    """
    Merges content of two dictionaries including merging of lists and returns results
    :param first_dictionary: First dictionary
    :param second_dictionary: Second dictionary
    :param overwrite: If values are primitive whether to overwrite first dictionary value.
    :return: Merged dictionary result. If values were lists, lists are merged.
    """
    def _merge_dictionaries(d1, d2, replace):
        for key, value in d2.items():
            if key not in d1:
                d1[key] = value
            elif isinstance(d1[key], list) and isinstance(value, list):
                d1[key] += value
            elif isinstance(d1[key], dict):
                _merge_dictionaries(d1[key], value, replace)
            elif replace:
                d1[key] = value

    _first_dictionary = copy.deepcopy(first_dictionary)
    _merge_dictionaries(_first_dictionary, second_dictionary, overwrite)
    return _first_dictionary


def find_remote_sibling(location, name):
    folder = path.join(location, name)
    if path.exists(folder):
        return folder
    elif location == '/':
        return None
    else:
        return find_remote_sibling(path.dirname(location), name)


class FileSystemError(Exception):
    pass


def copy_if_not_exist(source, target):
    if path.exists(target):
        return
    if not path.exists(source):
        raise FileSystemError('{name} does not exist.'.format(name=source))
    shutil.copy2(source, target)
