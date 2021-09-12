# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class UpdateLessonResult:
    def __init__(self):
        self._lesson_edit_id = None
        self._result = None

    @property
    def lesson_edit_id(self):
        """
        :return:mixed
        """
        return self._lesson_edit_id

    @lesson_edit_id.setter
    def lesson_edit_id(self, lesson_edit_id):
        """
        :param lesson_edit_id:
        """
        self._lesson_edit_id = lesson_edit_id

    @property
    def result(self):
        """
        :return:mixed
        """
        return self._result

    @result.setter
    def result(self, result):
        """
        :param result:
        """
        self._result = result
