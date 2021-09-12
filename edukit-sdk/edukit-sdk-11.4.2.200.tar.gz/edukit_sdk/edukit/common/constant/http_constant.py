#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class HttpConstant:
    # 请求头
    CONTENT_TYPE = 'Content-Type'
    APPLICATION_JSON = 'application/json'
    MULTIPART_FROM_DATA = 'multipart/form-data'
    APPLICATION_URLENCODED = 'application/x-www-form-urlencoded'
    HEAD_AUTHORIZATION = 'Authorization'
    HEAD_CLIENT_ID = 'client_id'
    HEAD_USER_AGENT = 'User-Agent'

    # 请求方法
    REQUEST_METHOD_GET = 'GET'
    REQUEST_METHOD_POST = 'POST'
    REQUEST_METHOD_PUT = 'PUT'
    REQUEST_METHOD_DELETE = 'DELETE'

    # curl配置
    VERIFYHOST_TYPE_COMMON_NAME = 1
    VERIFYHOST_TYPE_MATCH_HOST_NAME = 2
