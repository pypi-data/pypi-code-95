#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/9/7 10:41 上午
# @Author  : Hubert Shelley
# @Project  : starlette_utils
# @FileName: base.py
# @Software: PyCharm
"""
from smart7_orm.models.model import LogicDeleteModel


class Model(LogicDeleteModel):
    """模型基类"""

    class Meta:
        abstract = True
