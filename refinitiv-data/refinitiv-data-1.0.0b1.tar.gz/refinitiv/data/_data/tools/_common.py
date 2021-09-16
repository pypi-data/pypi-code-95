from enum import Enum
from typing import Any, Union
from typing import Optional

import numpy as np


def get_from_path(obj, path, delim="."):
    if isinstance(path, list):
        splitted = path

    else:
        splitted = path.split(delim)

    for k in splitted:
        if hasattr(obj, "get"):
            obj = obj.get(k)

        elif iterable(obj) and is_int(k):
            try:
                obj = obj[int(k)]
            except (IndexError, KeyError) as e:
                return None

    return obj


def is_int(obj):
    if isinstance(obj, str):
        try:
            int(obj)
        except Exception:
            return False
        else:
            return True
    return isinstance(obj, int)


def iterable(obj):
    if isinstance(obj, str):
        return False
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True


def urljoin(*pieces):
    # first piece have a leading slash
    if pieces and len(pieces[0]) > 1 and pieces[0][0] == "/":
        pieces = ("/",) + pieces
    # last piece have a trailing slash
    if pieces and len(pieces[-1]) > 1 and pieces[-1][-1] == "/":
        pieces = pieces + ("/",)
    return "/".join(s.strip("/") for s in pieces)


def is_any_defined(*args):
    return any(args)


def is_all_defined(*args):
    return all(args)


def is_all_same_type(item_type, items):
    return all(isinstance(item, item_type) for item in items)


def make_counter():
    i = 0

    def counter():
        nonlocal i
        i += 1
        return i

    return counter


def get_response_reason(response):
    if hasattr(response, "reason_phrase"):
        return response.reason_phrase
    elif hasattr(response, "reason"):
        return response.reason
    return "unknown reason"


class cached_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result


def is_tuple(what):
    return type(what) == tuple


def is_all_str(input_list: list) -> bool:
    return all([isinstance(i, str) for i in input_list])


def args_parser(param: Any, expect_none: bool = False) -> Optional[list]:
    if isinstance(param, str):
        return [param]

    if isinstance(param, list):
        if is_all_str(param):
            return param
        else:
            raise ValueError(f"Not all elements are strings in {param}")

    if param is None and expect_none:
        return None

    raise ValueError(f"Invalid type, expected str or list:\n {type(param)} is given")


class ArgsParser:
    def __init__(self, parse) -> None:
        self.parse = parse

    def get_str(self, *args, delim=None) -> str:
        if delim is not None:
            retval = delim.join(str(item) for item in self.get_list(*args))
        else:
            retval = self.parse(*args)
            retval = str(retval)
        return retval

    def get_list(self, *args) -> list:
        retval = self.parse(*args)
        if not isinstance(retval, list):
            retval = [retval]
        return retval

    def get_float(self, *args) -> float:
        retval = self.parse(*args)
        if isinstance(retval, np.datetime64):
            retval = retval.astype(float)
        else:
            retval = float(retval)
        return retval


def parse_list_of_str(param: Union[str, list]) -> list:
    if isinstance(param, str):
        return [param]

    if isinstance(param, list):
        if is_all_same_type(str, param):
            return param
        else:
            raise ValueError(f"Not all elements are strings in {param}")

    raise ValueError(f"Invalid type, expected str or list:{type(param)} is given")


def make_parse_enum(enum_class: iterable, can_be_lower: bool = False) -> callable:
    enum_values = [k.value for k in enum_class]

    def parse_enum(param: Union[str, list, Enum]) -> Union[str, list]:
        if isinstance(param, list):
            return [parse_enum(p) for p in param]

        if isinstance(param, enum_class):
            return param.value

        if param in enum_values:
            return param

        if can_be_lower and hasattr(param, "upper"):
            param_upper = param.upper()
            if param_upper in enum_values:
                return param_upper

        raise AttributeError(f"Value '{param}' must be in {enum_values}")

    return parse_enum


fields_arg_parser = ArgsParser(parse_list_of_str)
universe_arg_parser = fields_arg_parser


def make_enum_arg_parser(*args, **kwargs):
    return ArgsParser(make_parse_enum(*args, **kwargs))
