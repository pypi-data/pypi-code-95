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

    def __init__(self, detail: str = None, status_code: int = 502):
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

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        # For validation failures, we may collect many errors together,
        # so the details should always be coerced to a list if not already.
        if isinstance(detail, tuple):
            detail = list(detail)
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]

        self.detail = self._get_error_details(detail, code)

    def _get_error_details(self, detail, code):
        return detail
