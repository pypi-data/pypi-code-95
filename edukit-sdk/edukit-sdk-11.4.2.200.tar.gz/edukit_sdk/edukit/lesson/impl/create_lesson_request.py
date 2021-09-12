# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class CreateLessonRequest:
    def __init__(self):
        self._display_order = None
        self._catalogue_id = None

    @property
    def display_order(self):
        """
        :return:mixed
        """
        return self._display_order

    @display_order.setter
    def display_order(self, display_order):
        """
        :param display_order:
        """
        self._display_order = display_order

    @property
    def catalogue_id(self):
        return self._catalogue_id

    @catalogue_id.setter
    def catalogue_id(self, catalogue_id):
        self._catalogue_id = catalogue_id

    def to_bytes(self):
        """
        将对象转为JSON类型的字节
        :return:bytes
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)), 'utf-8')
