#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2021/7/20 10:00 下午
# @Author  : Hubert Shelley
# @Project  : microservice--registry-module
# @FileName: response_results.py
# @Software: PyCharm
"""
from starlette.responses import JSONResponse


class ResponseDict(dict):
    """
    响应基类
    """

    def __init__(self, data: dict = None, code: int = 0, message: str = ''):
        super().__init__(
            data=data,
            code=code,
            message=message,
            isSuccess=code == 0,
        )


def response_result(data: dict = None, message: str = 'ok', code: int = 0, status_code: int = 200):
    """
    请求结果

    :param data:
    :param message:
    :param code:
    :param status_code:
    :return:
    """
    return JSONResponse(ResponseDict(data=data, message=message, code=code), status_code=status_code)


def success_result(data: dict = None):
    """
    成功响应结果

    :param data:
    :return:
    """
    return response_result(data=data)


def error_result(message: str = 'failed', code: int = 1001, status_code: int = 502, data: dict = None):
    """
    失败响应结果

    :param data:
    :param message:
    :param code:
    :param status_code:
    :return:
    """
    return response_result(message=message, code=code, status_code=status_code, data=data)


def not_found_result(message: str = 'url not found', code: int = 1404, status_code: int = 404):
    """
    接口不存在响应结果

    :param message:
    :param code:
    :param status_code:
    :return:
    """
    return response_result(message=message, code=code, status_code=status_code)
