# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class ChangeCourseStatusRequest:
    def __init__(self, action=None, remarks=None, removal_reason=None):
        self._action = action
        self._remarks = remarks
        self._removal_reason = removal_reason

    @property
    def remarks(self):
        return self._remarks

    @remarks.setter
    def remarks(self, remarks):
        self._remarks = remarks

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, action):
        self._action = action

    @property
    def removal_reason(self):
        return self._removal_reason

    @removal_reason.setter
    def removal_reason(self, removal_reason):
        self._removal_reason = removal_reason

    def to_bytes(self):
        """
        将对象转为JSON类型的字节
        :return:bytes
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)), 'utf-8')
