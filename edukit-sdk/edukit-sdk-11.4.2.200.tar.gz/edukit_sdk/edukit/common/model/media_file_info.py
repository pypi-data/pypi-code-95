#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class MediaFileInfo:
    def __init__(self):
        self._path = None
        self._file_type = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def file_type(self):
        return self._file_type

    @file_type.setter
    def file_type(self, file_type):
        self._file_type = file_type
