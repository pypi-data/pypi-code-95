# -*- coding = UTF-8 -*-
# Author   :buxiubuzhi
# time     :2020/2/13  14:44
# ---------------------------------------
from typing import List

from ruamel import yaml


class Page:
    Document = ""
    Element = ""
    Type = ""

    def __init__(self, **kwargs):
        self.Element = kwargs["ele"]


class Source:
    page = {}

    def __init__(self, **kwargs):
        self.page = kwargs["page"]

    def GetAllKey(self) -> List:
        keys = [i for i in self.page]
        return keys

    def GetElement(self, key: str) -> Page:
        return Page(**self.page[key])


def GetElementSource(path: str) -> Source:
    """读取yaml文件"""
    with open(path, 'r', encoding='UTF-8') as fp:
        yaml_data = yaml.safe_load(fp)
    return Source(**yaml_data)



