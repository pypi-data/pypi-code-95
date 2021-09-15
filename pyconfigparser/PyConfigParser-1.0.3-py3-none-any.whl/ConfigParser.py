from typing import Optional
from abc import ABCMeta, abstractmethod
import json
import yaml
from pprint import pprint
from ._DictItem import DictItem


_data_loader = {
    "json": json.load,
    "yaml": yaml.safe_load
}

_data_saver = {
    "json": json.dump,
    "yaml": yaml.dump
}

_available_extensions = ("json", "yaml")


def _get_extension(filename: str):
    return filename.split(".")[-1]


class ConfigParser:
    def __init__(self, filename: str = None):
        if filename is None:
            self.FILENAME = None
            self.EXT = None
        else:
            self.FILENAME = filename
            self.EXT = _get_extension(filename)
            assert self.EXT in _available_extensions
            self._load()

    def _load(self):
        data = _data_loader[self.EXT](open(self.FILENAME, "r"))

        for k, v in data.items():
            if isinstance(v, dict):
                self.__dict__[k] = DictItem(v)
            else:
                self.__dict__[k] = v

    def as_dict(self) -> dict:
        result = {}
        for k, v in self.__dict__.items():
            if isinstance(v, (DictItem, ConfigParser)):
                result[k] = v.as_dict()
            else:
                result[k] = v

        del result["FILENAME"]
        del result["EXT"]
        return result

    def __str__(self):
        text = ""
        for k, v in self.__dict__.items():
            if isinstance(v, DictItem):
                text += f"{k} : {v.to_text(2)}\n"
            else:
                text += f"{k} : {v}\n"

        return text
     
    def write(self, filename: Optional[str] = None):
        assert not (self.FILENAME is None and filename is None)
        filename = self.FILENAME if filename is None else filename
        _data_saver[_get_extension(filename)](self.as_dict(), open(filename, "w"))
