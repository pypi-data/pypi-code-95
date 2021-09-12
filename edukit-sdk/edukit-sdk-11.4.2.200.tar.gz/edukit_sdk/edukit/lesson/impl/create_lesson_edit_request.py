# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class CreateLessonEditRequest:
    def __init__(self):
        self._force_create_new_edit = None

    @property
    def force_create_new_edit(self):
        """
        :return:mixed
        """
        return self._force_create_new_edit

    @force_create_new_edit.setter
    def force_create_new_edit(self, force_create_new_edit):
        """
        :param force_create_new_edit:
        """
        self._force_create_new_edit = force_create_new_edit

    def to_bytes(self):
        """
        将对象转为JSON类型的字节
        :return:bytes
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)), 'utf-8')
