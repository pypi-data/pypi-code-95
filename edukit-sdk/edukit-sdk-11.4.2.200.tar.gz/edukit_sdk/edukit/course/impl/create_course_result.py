# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class CreateCourseResult:
    def __init__(self, edit_id=None, course_id=None, result=None):
        self._edit_id = edit_id
        self._course_id = course_id
        self._result = result

    @property
    def edit_id(self):
        return self._edit_id

    @edit_id.setter
    def edit_id(self, edit_id):
        self._edit_id = edit_id

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, result):
        self._result = result

    @property
    def course_id(self):
        return self._course_id

    @course_id.setter
    def course_id(self, course_id):
        self._course_id = course_id
