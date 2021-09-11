#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/9/10 2:24 下午
# @Author  : Hubert Shelley
# @Project  : starlette_utils
# @FileName: core.py
# @Software: PyCharm
"""
import datetime
import jwt

from starlette_utils.exception import exceptions
from . import jwt_settings


class Token:
    token_type: str = None
    lifetime: int = None
    key: str = jwt_settings.JWT_SECRET_KEY
    algorithm: str = jwt_settings.JWT_ALGORITHM
    issuer: str = jwt_settings.JWT_ISSUER

    def __init__(self, token: str = None, verify: bool = True):
        self.payload = {}
        self.current_time = datetime.datetime.utcnow()
        if token:
            _token = token.split(' ')
            if _token.__len__() != 2:
                raise exceptions.TokenErrorException()
            if _token[0] != self.token_type:
                raise exceptions.TokenTypeException()
            self.token = _token[1]
            if verify:
                self.valid()
        else:
            self.payload["token_type"] = self.token_type
            if self.lifetime:
                self.set_exp()
            if self.issuer:
                self.payload['iss'] = self.issuer

    def __repr__(self):
        return repr(self.payload)

    def __getitem__(self, key):
        return self.payload[key]

    def __setitem__(self, key, value):
        self.payload[key] = value

    def __delitem__(self, key):
        del self.payload[key]

    def __contains__(self, key):
        return key in self.payload

    def valid(self):
        try:
            self.payload = jwt.decode(self.token, key=self.key, algorithms=[self.algorithm])
        except Exception as e:
            raise e

    def set_exp(self, claim='exp', from_time: datetime = None, lifetime: int = None):
        """
        Updates the expiration time of a token.
        """
        if from_time is None:
            from_time = self.current_time

        if lifetime is None:
            lifetime = self.lifetime

        self.payload[claim] = from_time + datetime.timedelta(seconds=lifetime)

    def __str__(self):
        """
        Signs and returns a token as a base64 encoded string.
        """
        return jwt.encode(self.payload, key=self.key, algorithm=self.algorithm)
