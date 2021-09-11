#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/5/24 下午3:54
# @Author  : Hubert Shelley
# @Project  : Smart7_ORM
# @FileName: MySQL.py
# @Software: PyCharm
"""
from smart7_orm.db.base import SQLBase


class MySQL(SQLBase):
    def get_name(self) -> str:
        return 'mysql'

    def get_port(self) -> int:
        return self.port if self.port else 3306
