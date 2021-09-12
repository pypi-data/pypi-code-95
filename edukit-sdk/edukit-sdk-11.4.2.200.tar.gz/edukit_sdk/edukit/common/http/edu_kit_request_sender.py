#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging

from edukit_sdk.edukit.common.auth.auth_token_credential import \
    AuthTokenCredential
from edukit_sdk.edukit.common.config.config import Config
from edukit_sdk.edukit.common.constant.client_constant import ClientConstant
from edukit_sdk.edukit.common.constant.http_constant import HttpConstant
from edukit_sdk.edukit.common.http.client import Client
from edukit_sdk.edukit.common.http.request import Request


class EduKitRequestSender:
    def __init__(self, credential_list: dict):
        self._client = Client()
        config = Config()
        self._agent = config.get_config().get(
            ClientConstant.SDK_NAME) + '-' + config.get_config().get(
                ClientConstant.SDK_VERSION)
        self._domain = config.get_domain()
        self._credential_list = credential_list
        self._log_info_prefix = ClientConstant.REQUESTING

    def post(self, url, body=None, headers=None, form_data=None, params=None):
        """
        post请求
        :param url: 请求url
        :param body: 请求体
        :param headers: 请求头,如果传入为空,则默认为是application/json
        :param form_data: 非文件数据
        :param params:
        :return:
        """
        request = self.build_request(method=HttpConstant.REQUEST_METHOD_POST,
                                     headers=headers,
                                     url=url,
                                     body=body,
                                     form_data=form_data,
                                     params=params)
        logging.info(self._log_info_prefix + request.url)
        return self._client.send_request(request)

    def put(self, url, body=None, headers=None):
        request = self.build_request(method=HttpConstant.REQUEST_METHOD_PUT,
                                     headers=headers,
                                     url=url,
                                     body=body)
        logging.info(self._log_info_prefix + request.url)
        return self._client.send_request(request)

    def get(self, url, headers=None, body=None, params=None):
        request = self.build_request(method=HttpConstant.REQUEST_METHOD_GET,
                                     headers=headers,
                                     url=url,
                                     body=body,
                                     form_data=None,
                                     params=params)
        logging.info(self._log_info_prefix + request.url)
        return self._client.send_request(request)

    def delete(self, url, headers=None, body=None):
        request = self.build_request(method=HttpConstant.REQUEST_METHOD_DELETE,
                                     headers=headers,
                                     url=url,
                                     body=body)
        logging.info(self._log_info_prefix + request.url)
        return self._client.send_request(request)

    def upload_once(self, url, headers, body, method):
        return self._client.send_request(
            Request(url=url, method=method, headers=headers, body=body))

    def build_request(self,
                      method,
                      headers,
                      url,
                      body,
                      form_data=None,
                      params=None):
        """
        @param method 请求方法
        @param headers 请求头,如果传入为None,则返回为application/json
        @param url 请求url
        @param body 请求体(如果是上传文件,包含要传入的二进制数据)
        @param form_data 非文件数据
        @param params
        @return Request
        """
        auth_token_credential = AuthTokenCredential(self._credential_list)
        token = auth_token_credential.get_token()
        if not headers:
            headers = dict()
        headers[HttpConstant.HEAD_AUTHORIZATION] = 'Bearer ' + token
        headers[HttpConstant.
                HEAD_CLIENT_ID] = auth_token_credential.get_client_id()
        headers[HttpConstant.HEAD_USER_AGENT] = self._agent
        if not headers.get(HttpConstant.CONTENT_TYPE):
            headers[HttpConstant.CONTENT_TYPE] = HttpConstant.APPLICATION_JSON
        url = self._domain + url

        return Request(url, method, headers, body, form_data, params)
