#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import os
import uuid

from edukit_sdk.edukit.common.constant.api_constant import ApiConstant
from edukit_sdk.edukit.common.constant.client_constant import ClientConstant
from edukit_sdk.edukit.common.constant.error_constant import ErrorConstant
from edukit_sdk.edukit.common.constant.file_upload_constant import \
    FileUploadConstant
from edukit_sdk.edukit.common.constant.http_constant import HttpConstant
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.http.http_common_response import \
    HttpCommonResponse


def build_form_data(form_data: dict):
    """
    生成上传文件所需的form-data格式
    :param form_data: 传入的需要上传的字典
    :return:bytes
    """
    delimiter = str(uuid.uuid1()).replace('-', '')  # 将uuid转化为字符串
    headers = {
        HttpConstant.CONTENT_TYPE: 'multipart/form-data; boundary=' + delimiter
    }

    data1 = ''
    eol = os.linesep
    file_content = form_data.get('file')
    if file_content:
        del form_data['file']
    for name, content in form_data.items():
        data1 += "--" + delimiter + eol + \
                 'Content-Disposition: form-data; name="' \
                 + name + '"' + eol + eol \
                 + str(content) + eol
    # 拼接文件流
    data1 += "--" + delimiter + eol + \
             'Content-Disposition: form-data; name="file"; filename="' + \
             form_data.get(
                 ClientConstant.FILE_NAME) + '"' \
             + eol + 'Content-Type:application/octet-stream' \
             + eol + eol

    data3 = eol + "--" + delimiter + "--" + eol
    body = bytes(data1, ClientConstant.UTF_8) + file_content + bytes(
        data3, ClientConstant.UTF_8)
    # 返回二进制数据
    return body, headers


class UploadPicture:
    def __init__(self, file_request, request_sender):
        self._file_request = file_request
        self._request_sender = request_sender

    def upload(self):
        url = ApiConstant.UPLOAD_RESOURCE_URL
        # 获取图片后缀
        suffix = os.path.splitext(self._file_request.path)[-1]
        # 图片格式只能是jpg,png中的一种
        if suffix not in FileUploadConstant.PICTURE_SUFFIX:
            raise EduKitException('Upload failed! ErrorMessage:{}'.format(
                ErrorConstant.PICTURE_FILE_TYPE_ERROR))

        # 将图片读取为二进制数据
        with open(self._file_request.path, ClientConstant.RB) as f:
            file = f.read()
            form_data = {
                ClientConstant.FILE_SIZE: self._file_request.file_size,
                ClientConstant.FILE_SHA256: self._file_request.sha256,
                ClientConstant.RESOURCE_TYPE: self._file_request.resource_type,
                ClientConstant.FILE_NAME: self._file_request.file_name,
                ClientConstant.FILE: file
            }
            body, headers = build_form_data(form_data)
        try:
            rsp = HttpCommonResponse(
                self._request_sender.post(url=url, body=body, headers=headers))
        except EduKitException as e:
            raise EduKitException(e.message)

        return rsp.get_rsp()
