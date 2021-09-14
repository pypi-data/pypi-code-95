#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/9/10 11:57 上午
# @Author  : Hubert Shelley
# @Project  : starlette_utils
# @FileName: settings.py
# @Software: PyCharm
"""

JWT_ISSUER = None
JWT_PASS_TIME = 7200
JWT_REFRESH_PASS_TIME = 604800
JWT_SECRET_KEY = '123456'
JWT_ALGORITHM = 'HS256'

try:
    from settings import *
except ImportError:
    pass
