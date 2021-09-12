#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import os
import ssl
from urllib import request as request_kit

from edukit_sdk.edukit.common.config.config import Config
from edukit_sdk.edukit.common.constant.client_constant import ClientConstant
from edukit_sdk.edukit.common.constant.common_constant import CommonConstant
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.http.client_response import ClientResponse


def ssl_certificate():
    # ssl验证
    ssl_path = os.path.join(CommonConstant.ROOT_PATH, CommonConstant.AUTH_DIR)
    certificate_path = os.path.join(CommonConstant.ROOT_PATH,
                                    CommonConstant.AUTH_DIR,
                                    CommonConstant.CERT)

    if not os.path.exists(certificate_path):
        if not os.path.exists(ssl_path):
            os.makedirs(ssl_path)
        cert = request_kit.urlopen(
            CommonConstant.DEFAULT_CERT_URL).read().decode(
                ClientConstant.UTF_8)
        with open(certificate_path,
                  CommonConstant.FILE_MODE_CREDENTIAL_WRITE,
                  encoding=ClientConstant.UTF_8) as fcertificate:
            os.chmod(certificate_path, CommonConstant.FILE_DEFAULT_MOD)
            fcertificate.write(cert)

    # 生成SSL上下文
    context = ssl.create_default_context()
    # 加载信任根证书
    context.load_verify_locations(certificate_path)
    return context


class Client:
    def __init__(self):
        config = Config()
        self._connectTimeout = config.get_config().get('CONNECT_TIMEOUT')
        self._operationTimeout = config.get_config().get('OPERATION_TIMEOUT')

    def send_request(self, request):
        """
        发送请求
        :param request: 请求内容
        :return:
        """
        data = request.body if request.body else None

        headers = request.headers

        # ssl验证
        ssl_context = ssl_certificate()

        # 发送请求
        request_box = request_kit.Request(url=request.url,
                                          data=data,
                                          headers=headers,
                                          method=request.method)
        # 请求异常捕获
        try:
            response = request_kit.urlopen(request_box,
                                           context=ssl_context,
                                           timeout=int(self._connectTimeout))
            body = str(response.read(), encoding=ClientConstant.UTF_8)
            rsp_code = response.status
            headers = response.headers
            return ClientResponse(rsp_code, headers, body, None)
        except Exception as e:
            raise EduKitException(str(e))
