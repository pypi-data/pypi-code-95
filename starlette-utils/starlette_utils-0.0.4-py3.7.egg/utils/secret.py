#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/9/9 10:33 上午
# @Author  : Hubert Shelley
# @Project  : starlette_utils
# @FileName: secrets.py
# @Software: PyCharm
"""
import hashlib
import hmac
import secrets


def get_secrets_key(length: int):
    """
    生成随机密钥

    :param length:
    :return:
    """
    return secrets.token_hex(length)[0:length]


def make_password(password: str, salt: [str, bytes]):
    """
    创建密码

    :param password: 密码
    :param salt:
    :return:
    """
    if isinstance(salt, str):
        salt = salt.encode()
    _ = hmac.new(salt, digestmod=hashlib.sha256)
    _.update(password.encode())
    return _.hexdigest()


def check_password(origin_password: str, password: str, salt: [str, bytes]):
    """
    校验密码

    :param origin_password: 原密码
    :param password: 密文
    :param salt:
    :return:
    """
    if isinstance(salt, str):
        salt = salt.encode()
    _ = hmac.new(salt, digestmod=hashlib.sha256)
    _.update(origin_password.encode())
    return _.hexdigest() == password
