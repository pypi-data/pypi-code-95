#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class TeacherBasicInfo:
    def __init__(self):
        self._dev_teacher_id = None

    @property
    def dev_teacher_id(self):
        """
        :return: mixed
        """
        return self._dev_teacher_id

    @dev_teacher_id.setter
    def dev_teacher_id(self, dev_teacher_id):
        """
        由您指定的教师编号
        :param dev_teacher_id:
        :return:
        """
        self._dev_teacher_id = dev_teacher_id

    def to_json_string(self):
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
