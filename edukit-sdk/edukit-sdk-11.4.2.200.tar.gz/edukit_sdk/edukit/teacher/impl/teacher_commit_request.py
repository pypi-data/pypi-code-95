#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class TeacherCommitRequest:
    def __init__(self):
        self._teacher_id = None,
        self._edit_id = None,

    @property
    def teacher_id(self):
        return self._teacher_id

    @teacher_id.setter
    def teacher_id(self, teacher_id):
        self._teacher_id = teacher_id

    @property
    def edit_id(self):
        return self._edit_id

    @edit_id.setter
    def edit_id(self, edit_id):
        self._edit_id = edit_id

    def to_json_string(self):
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
