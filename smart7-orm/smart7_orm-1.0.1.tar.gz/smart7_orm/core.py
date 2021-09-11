#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/5/24 下午3:49
# @Author  : Hubert Shelley
# @Project  : Smart7_ORM
# @FileName: core.py
# @Software: PyCharm
"""
from copy import copy

from smart7_orm import db
from smart7_orm import orm_settings as settings


def make_sql() -> db.Base:
    database = copy(settings.database)
    db_class = getattr(db, database.pop('db'))
    return db_class(**database)
