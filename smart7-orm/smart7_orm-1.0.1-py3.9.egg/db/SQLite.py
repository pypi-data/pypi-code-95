#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/5/24 下午3:55
# @Author  : Hubert Shelley
# @Project  : Smart7_ORM
# @FileName: SQLite.py
# @Software: PyCharm
"""
from .base import SQLiteBase


class SQLite(SQLiteBase):
    def get_name(self) -> str:
        return 'sqlite'
