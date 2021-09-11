#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/9/8 10:06 上午
# @Author  : Hubert Shelley
# @Project  : smart7-orm
# @FileName: orm_settings.py
# @Software: PyCharm
"""
# mysql setting
# database = {
#     "db": 'MySQL',
#     "host": "localhost",
#     "username": "hubert",
#     "password": "hubert",
#     "db_name": "test_table",
# }

# sqlite setting
database = {
    "db": 'SQLite',
    "db_name": "test_table.db",
}

LOG_MAX_SIZE = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 5

try:
    from settings import *
except ImportError:
    pass
