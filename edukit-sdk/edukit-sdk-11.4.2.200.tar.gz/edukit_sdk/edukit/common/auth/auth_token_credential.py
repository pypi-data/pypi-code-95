#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json
import logging
import time

from edukit_sdk.edukit.common.config.config import Config
from edukit_sdk.edukit.common.constant.api_constant import ApiConstant
from edukit_sdk.edukit.common.constant.client_constant import ClientConstant
from edukit_sdk.edukit.common.constant.common_constant import CommonConstant
from edukit_sdk.edukit.common.constant.error_constant import ErrorConstant
from edukit_sdk.edukit.common.constant.http_constant import HttpConstant
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.http.client import Client
from edukit_sdk.edukit.common.http.request import Request


class AuthTokenCredential:
    token_memory = {}

    def __init__(
        self,
        credential_list: dict,
        client=None,
    ):
        credential = self.__get_client(credential_list)
        self._token = AuthTokenCredential.token_memory.get('access_token')
        self._expire = AuthTokenCredential.token_memory.get('cached_expire')
        self._client_id = credential.get('client_id')
        self._client_secret = credential.get('client_secret')
        config = Config()
        self._domain = config.get_domain()
        if client is None:
            self._client = Client()
        else:
            self._client = client

    def get_client_id(self):
        return self._client_id

    def get_token(self):
        cached_client_id = AuthTokenCredential.token_memory.get(
            'cached_client_id')
        cached_token = AuthTokenCredential.token_memory.get('cached_token')
        cached_expire = AuthTokenCredential.token_memory.get('cached_expire')
        cached_time = AuthTokenCredential.token_memory.get('cached_time')

        # 检测token是否有效,是否过期
        if self.__is_cached_token_valid(cached_client_id, cached_token,
                                        cached_expire, cached_time):
            logging.info('Got token from cache.')
            return cached_token
        try:
            self.__refresh_token()

            if not self._token:
                token_body = self.__obtain_token()
                if token_body:
                    self._token = token_body.get('access_token')
        except EduKitException as e:
            raise EduKitException('Get token failed! '
                                  'ErrorMessage:{}'.format(str(e)))

        return self._token

    def __refresh_token(self):
        """
        刷新token
        :return:
        """
        try:
            cached_client_id = AuthTokenCredential.token_memory.get(
                'cached_client_id')
            cached_token = AuthTokenCredential.token_memory.get('cached_token')
            cached_expire = AuthTokenCredential.token_memory.get(
                'cached_expire')
            cached_time = AuthTokenCredential.token_memory.get('cached_time')
            if self.__is_cached_token_valid(cached_client_id, cached_token,
                                            cached_expire, cached_time):
                logging.info('Access token has been refreshed.')
                return

            token_body = self.__obtain_token()
            if token_body:
                self._token = token_body.get('access_token')
                self._expire = token_body.get('expires_in')

                cached_token = {
                    'cached_client_id': self._client_id,
                    'cached_token': self._token,
                    'cached_expire': self._expire,
                    'cached_time': time.time()
                }

                AuthTokenCredential.token_memory = cached_token
        except EduKitException as e:
            raise EduKitException(str(e))

    def __obtain_token(self):
        url = self._domain + ApiConstant.TOKEN_URL
        body = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "client_credentials"
        }
        logging.info('Obtaining token from remote.')
        body = bytes(json.dumps(body), encoding=ClientConstant.UTF_8)
        headers = {HttpConstant.CONTENT_TYPE: HttpConstant.APPLICATION_JSON}
        try:
            rsp = self._client.send_request(
                Request(url=url,
                        method=HttpConstant.REQUEST_METHOD_POST,
                        headers=headers,
                        body=body))
            if rsp and not rsp.get_error() and rsp.get_rsp() and rsp.get_rsp(
            ).get('error') == CommonConstant.RESULT_SUCCESS:
                return rsp.get_rsp()
        except Exception as e:
            raise EduKitException(str(e))

    def __get_client(self, credential_list):
        """
        获取用户信息
        :param credential_list: 包含client_id和client_secret
        :return:
        """
        if self.__is_credential_valid(credential_list):
            return credential_list
        raise EduKitException(ErrorConstant.CREDENTIAL_IS_EMPTY)

    def __is_cached_token_valid(self, cached_client_id, cached_token,
                                cached_expire, cached_token_time) -> bool:
        """
        缓存的token是否有效,True为有效
        :param cached_client_id: 缓存token对应的用户id
        :param cached_token: 缓存token
        :param cached_expire: 设置的缓存过期时间(默认为2天)
        :param cached_token_time: 缓存token时的时间
        :return:
        """
        if all([cached_client_id, cached_token, cached_expire,
                cached_token_time]) \
                and cached_client_id == self._client_id \
                and time.time() - cached_token_time < \
                int(cached_expire) - CommonConstant\
                .REFRESH_TIME_BEFORE_EXPIRE:
            return True
        return False

    @staticmethod
    def __is_credential_valid(credential_list) -> bool:
        """
        传入的用户信息是否正确
        :param credential_list: 用户信息,包含client_id和client_secret
        :return:
        """
        return credential_list.get('client_id') and credential_list.get(
            'client_secret')
