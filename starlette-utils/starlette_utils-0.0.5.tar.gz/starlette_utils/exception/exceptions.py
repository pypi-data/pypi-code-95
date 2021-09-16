#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/7/20 10:27 下午
# @Author  : Hubert Shelley
# @Project  : microservice--registry-module
# @FileName: exceptions.py
# @Software: PyCharm
"""
from starlette.exceptions import HTTPException


class HttpException(HTTPException):
    """
    响应异常基类
    """
    default_code = 1001

    def __init__(self, detail: [str, dict] = None, status_code: int = 502):
        super().__init__(status_code=status_code, detail=detail)


class ApiException(HttpException):
    """
    Api响应异常基类
    """
    status_code = 500
    default_detail = '响应异常'
    default_code = 1001

    def __init__(self, detail=None, status_code=None):
        super().__init__(status_code=status_code or self.status_code, detail=detail or self.default_detail)


class NotFondException(ApiException):
    """
    资源不存在
    """
    status_code = 502
    default_detail = '资源不存在'
    default_code = 1020

    def __init__(self, detail=None, status_code=None):
        super().__init__(status_code=status_code or self.status_code, detail=detail or self.default_detail)


class MultipleFondException(ApiException):
    """
    资源重复
    """
    status_code = 502
    default_detail = '资源重复'
    default_code = 1021

    def __init__(self, detail=None, status_code=None):
        super().__init__(status_code=status_code or self.status_code, detail=detail or self.default_detail)


class ValidationError(ApiException):
    status_code = 503
    default_detail = '序列化校验失败'
    default_code = 1010
    data = {}

    def __init__(self, detail=None, status_code=None, data: dict = None):
        self.data = data
        super().__init__(status_code=status_code or self.status_code, detail=detail or self.default_detail)


class TokenErrorException(ApiException):
    """
    Token字符异常
    """
    status_code = 502
    default_detail = 'Token字符异常'
    default_code = 1030

    def __init__(self, detail=None, status_code=None):
        super().__init__(status_code=status_code or self.status_code, detail=detail or self.default_detail)


class TokenTypeException(ApiException):
    """
    Token类型出错
    """
    status_code = 502
    default_detail = 'Token类型出错'
    default_code = 1031

    def __init__(self, detail=None, status_code=None):
        super().__init__(status_code=status_code or self.status_code, detail=detail or self.default_detail)
