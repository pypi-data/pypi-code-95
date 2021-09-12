#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException


class ClientResponse:
    def __init__(self, code, headers=None, body=None, error=None):
        self.statusCode = code
        self.headers = headers
        self.body = body
        self.error = error
        self.rsp_data = None

        if error:
            return

        if not body:
            if code >= 400:
                raise EduKitException('http request status code is %s' % code)
        else:
            self.rsp_data = json.loads(body)
        if code >= 400:
            self.error = self.rsp_data

    def get_error(self):
        return self.error

    def get_headers(self):
        return self.headers

    def get_rsp(self):
        return self.rsp_data
