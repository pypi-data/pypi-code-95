#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.http.client_response import ClientResponse


class HttpCommonResponse:
    def __init__(self, source_response: ClientResponse):
        if source_response and source_response.get_error():
            raise EduKitException(source_response.get_error())
        if source_response:
            self._response = source_response.get_rsp()
            self._headers = source_response.get_headers()
        else:
            raise EduKitException("Request failed!")

    def get_rsp(self):
        return self._response

    def get_headers(self):
        return self._headers
