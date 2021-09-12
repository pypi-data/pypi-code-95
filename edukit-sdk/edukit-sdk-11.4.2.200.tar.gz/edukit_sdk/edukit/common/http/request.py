#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from urllib import parse

from edukit_sdk.edukit.common.constant.http_constant import HttpConstant


class Request:
    def __init__(self,
                 url,
                 method,
                 headers,
                 body,
                 form_data=None,
                 params=None):
        if params and isinstance(params, dict):
            url += '?' + parse.urlencode(params)
        if not headers:
            headers = {
                HttpConstant.CONTENT_TYPE: HttpConstant.APPLICATION_JSON
            }

        self.url = url
        self.method = method
        if not headers:
            headers = dict()
        self.headers = headers
        if not body:
            body = dict()
        self.body = body
        if not form_data:
            form_data = dict()
        self.form_data = form_data
