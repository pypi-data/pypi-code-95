#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging
import os
import re

from edukit_sdk.edukit.common.constant.client_constant import ClientConstant
from edukit_sdk.edukit.common.constant.error_constant import ErrorConstant
from edukit_sdk.edukit.common.constant.file_upload_constant import \
    FileUploadConstant
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.file_upload.file_upload_request import \
    FileUploadRequest
from edukit_sdk.edukit.common.file_upload.file_uploader_factory import \
    FileUploaderFactory
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender


class FileUpload:
    def __init__(
        self,
        path,
        request_sender: EduKitRequestSender,
        resource_type=None,
        file_type=None,
        public_file=False,
    ):
        """
        文件上传
        :param path: 上传的文件路径
        :param request_sender: 封装请求信息
        :param resource_type: 资源文件类型
        :param file_type: 媒体文件类型
        :param public_file:
        """
        self._file_request = FileUploadRequest(path=path,
                                               file_type=file_type,
                                               resource_type=resource_type,
                                               public_file=public_file)
        self._relative_path_pattern = FileUploadConstant.RELATIVE_PATH_PATTERN
        self._resource_type_dict = FileUploadConstant.RESOURCE_TYPE
        self.__get_init_object(path, file_type, resource_type, public_file)
        is_valid, message = self.__is_input_valid(path, resource_type,
                                                  file_type, public_file)
        self._request_sender = request_sender
        if not is_valid:
            logging.info(message)

    def get_file_info(self):
        return self._file_request

    def upload(self):
        file_uploader_factory = FileUploaderFactory(self._file_request,
                                                    self._request_sender)
        file_uploader = file_uploader_factory.get_file_uploader(
            self._file_request.resource_type)
        try:
            result = file_uploader.upload()
        except EduKitException as e:
            raise EduKitException(str(e))
        logging.info("Uploaded successfully!")
        return result

    def __is_input_valid(self, path, resource_type, file_type, public_file):
        """
        判断传入的参数是否符合要求
        :param path: 需要上传的文件路径
        :param resource_type: 资源文件类型
        :param file_type: 媒体文件类型
        :param public_file:
        :return:
        """
        is_valid = False
        message = ''

        if not path:
            message = ErrorConstant.PATH_NOT_NULL
            logging.info(message)
        if re.match(self._relative_path_pattern, path):
            message = ErrorConstant.PATH_NOT_ABSOLUTE
            return is_valid, message
        if not os.path.exists(path):
            message = ErrorConstant.FILE_NOT_EXISTS.format(
                self.get_logfile_path(resource_type, path))
            return is_valid, message
        if os.path.isdir(path):
            message = ErrorConstant.PATH_IS_DIRECTORY.format(path)
            return is_valid, message
        if resource_type:
            if file_type or public_file:
                message = ErrorConstant.FILE_TYPE_OR_PUBLIC_FILE_NOT_NULL
                return is_valid, message
            if resource_type not in self._resource_type_dict.values():
                message = ErrorConstant.RESOURCE_TYPE_IS_INVALID
                return is_valid, message
        else:
            if not file_type:
                message = ErrorConstant.FILE_TYPE_NO_VALUE
                return is_valid, message

        is_valid = True
        return is_valid, message

    @staticmethod
    def get_logfile_path(resource_type, path):
        return '' if resource_type == FileUploadConstant.RESOURCE_TYPE.get(
            ClientConstant.TUTOR_PORTRAIT) else path

    def __get_init_object(self, path, file_type, resource_type, public_file):
        self._file_request = FileUploadRequest(path, file_type, resource_type,
                                               public_file)
