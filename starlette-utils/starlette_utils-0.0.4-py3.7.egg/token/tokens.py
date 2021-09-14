#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/9/10 11:00 上午
# @Author  : Hubert Shelley
# @Project  : starlette_utils
# @FileName: jwt.py
# @Software: PyCharm
"""
import typing

from .core import Token
from . import jwt_settings


class AccessToken(Token):
    token_type = 'access'
    lifetime = jwt_settings.JWT_PASS_TIME


class RefreshToken(Token):
    token_type = 'refresh'
    access_token_class: typing.Type[Token] = AccessToken
    lifetime = jwt_settings.JWT_REFRESH_PASS_TIME

    no_copy_claims = (
        'token_type',
        'exp',
        'jti',
    )

    @property
    def access_token(self):
        access = self.access_token_class()

        access.set_exp(from_time=self.current_time)

        no_copy = self.no_copy_claims
        for claim, value in self.payload.items():
            if claim in no_copy:
                continue
            access[claim] = value

        return access
