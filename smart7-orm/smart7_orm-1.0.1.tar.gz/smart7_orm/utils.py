#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/9/8 10:36 上午
# @Author  : Hubert Shelley
# @Project  : smart7-orm
# @FileName: utils.py
# @Software: PyCharm
"""
import os
import re
import sys
import typing

from smart7_orm.core import make_sql
from smart7_orm.models import Model


def auto_discover_models(_model=Model) -> typing.List[str]:
    """
    自动发现模型所在modules

    :param _model: 模型基类
    :return:
    """
    if _model is Model:
        print("auto discover models start")
    _model_module_list = []
    for sub_class in _model.__subclasses__():
        if not sub_class._meta.abstract:
            _model_module_list.append(sub_class.__module__)
        if len(sub_class.__subclasses__()) > 0:
            _model_module_list.extend(auto_discover_models(sub_class))
    if _model is Model:
        print("all model discovered")
    return list(set(_model_module_list))


def discover_models() -> typing.List[str]:
    """
    自动发现模型

    :return:
    """
    for root, dirs, files in os.walk('.'):
        py_files = [_ for _ in files if re.match(r'[^\.]*.py', _)]
        if root == '.':
            try:
                py_files.remove(sys.argv[0].split('/')[-1])
            except Exception as e:
                pass
        if 'setup.py' in py_files:
            py_files.remove('setup.py')
        if py_files:
            for py_file in py_files:
                _path = f'{root}/{py_file[:-3]}'[2:].replace('/', '.')
                __import__(_path)
    return auto_discover_models()


def get_connection_url():
    return make_sql().get_url()


if __name__ == '__main__':
    print(discover_models())
