#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class TeacherCreateResult:
    def __init__(self):
        self._edit_id = None
        self._teacher_id = None
        self._result = None

    @property
    def edit_id(self):
        return self._edit_id

    @edit_id.setter
    def edit_id(self, edit_id):
        self._edit_id = edit_id

    @property
    def teacher_id(self):
        return self._teacher_id

    @teacher_id.setter
    def teacher_id(self, teacher_id):
        self._teacher_id = teacher_id

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, result):
        self._result = result
