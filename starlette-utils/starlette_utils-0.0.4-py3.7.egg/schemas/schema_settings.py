#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/9/10 11:57 上午
# @Author  : Hubert Shelley
# @Project  : starlette_utils
# @FileName: settings.py
# @Software: PyCharm
"""
from apispec.ext.marshmallow import MarshmallowPlugin

SCHEMA_CONFIG = {
    'title': "schema template",
    'version': "1.0",
    'openapi_version': "3.0.0",
    'info': {"description": "schema template"},
    'plugins': [],
    'consumes': ["application/json"],
}

try:
    from settings import *
except ImportError:
    pass

if not SCHEMA_CONFIG.get('plugins'):
    SCHEMA_CONFIG['plugins'] = [MarshmallowPlugin()]
elif MarshmallowPlugin not in [type(_) for _ in SCHEMA_CONFIG['plugins']]:
    marshmallow_plugin = MarshmallowPlugin()
    SCHEMA_CONFIG['plugins'].append(marshmallow_plugin)
