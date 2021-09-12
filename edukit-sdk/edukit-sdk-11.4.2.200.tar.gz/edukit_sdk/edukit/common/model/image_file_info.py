#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class ImageFileInfo:
    def __init__(self):
        self._path = None
        self._resource_type = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def resource_type(self):
        return self._resource_type

    @resource_type.setter
    def resource_type(self, resource_type):
        self._resource_type = resource_type
