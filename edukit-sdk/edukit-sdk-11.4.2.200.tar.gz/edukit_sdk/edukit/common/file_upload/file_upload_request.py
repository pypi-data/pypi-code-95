#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import os

from edukit_sdk.edukit.common.constant.error_constant import ErrorConstant
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.helpers.helpers import Helpers


class FileUploadRequest:
    def __init__(
        self,
        path,
        file_type=None,
        resource_type='-1',
        public_file='False',
    ):
        if not os.path.exists(path):
            raise EduKitException(ErrorConstant.FILE_NOT_EXISTS.format(path))
        self._path = path
        self._file_name = Helpers.get_file_base_name(
            path)  # 因为接口中filename带扩展名，故在此使用get_file_base_name()
        self._file_extension = Helpers.get_file_extension(path)
        self._file_size = Helpers.get_file_size(path)
        self._sha256 = Helpers.get_sha256(path)
        self._file_type = Helpers.get_mime(
            path) if not file_type else file_type
        self._resource_type = resource_type
        self._public_file = public_file

    @property
    def path(self):
        return self._path

    @property
    def file_name(self):
        return self._file_name

    @property
    def file_extension(self):
        return self._file_extension

    @property
    def file_size(self):
        return self._file_size

    @property
    def sha256(self):
        return self._sha256

    @property
    def file_type(self):
        return self._file_type

    @property
    def resource_type(self):
        return self._resource_type

    @property
    def public_file(self):
        return self._public_file
