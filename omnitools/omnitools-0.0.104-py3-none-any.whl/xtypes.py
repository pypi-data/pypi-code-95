from typing import *


__ALL__ = ["str_or_bytes", "list_or_dict", "list_or_tuple", "bytes_or_list", "key_pair_format", "color_value", "encryptedsocket_function", "Obj"]


str_or_bytes = Union[str, bytes]
list_or_dict = Union[list, dict]
list_or_tuple = Union[list, tuple]
bytes_or_list = Union[bytes, list]
key_pair_format = Dict[str, bytes]
color_value = Tuple[int, int, int]
encryptedsocket_function = Dict[str, Callable[[Any], Any]]


class Obj(object):
    """
    @DynamicAttrs
    """
    def __init__(self, a: dict) -> None:
        self.__org = a
        for b, c in a.items():
            if isinstance(c, (list, tuple)):
                setattr(self, b, self.__loop(c))
            else:
                setattr(self, b, Obj(c) if isinstance(c, dict) else c)

    def __loop(self, i: list_or_tuple) -> list_or_tuple:
        z = []
        for item in i:
            if isinstance(item, dict):
                z.append(Obj(item))
            elif isinstance(item, (list, tuple)):
                z.append(self.__loop(item))
            else:
                z.append(item)
        return z if isinstance(i, list) else tuple(z)

    def __str__(self):
        return self.dump()

    def dump(self, indent_scale: int = 4):
        from .js import dumpobj
        return dumpobj(self.__org, isObj=True, indent_scale=indent_scale)

