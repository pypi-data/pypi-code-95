from copy import deepcopy
from enum import Enum


def remove_key(value: dict, removed_key='self') -> dict:
    for k in removed_key.split(","):
        if k in value:
            value.pop(k)
    return value


def package_data(dict_data: dict, replace_keys: dict = None) -> dict:
    if replace_keys is None:
        replace_keys = dict()
    new_dict = deepcopy(dict_data)

    for k, v in dict_data.items():
        if v is None:
            new_dict.pop(k)
            continue
        if isinstance(v, Enum):
            new_dict[k] = v.value
        if k in replace_keys:
            new_dict[replace_keys[k]] = new_dict.pop(k)
    return new_dict
