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
    "path": ".sqlite.db",
}

LOG_MAX_SIZE = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 5

try:
    import importlib

    settings = importlib.import_module('settings')
    if hasattr(settings, 'database'):
        database = settings.database
    if hasattr(settings, 'LOG_MAX_SIZE'):
        LOG_MAX_SIZE = settings.LOG_MAX_SIZE
    if hasattr(settings, 'LOG_BACKUP_COUNT'):
        LOG_BACKUP_COUNT = settings.LOG_BACKUP_COUNT
except ImportError:
    pass
