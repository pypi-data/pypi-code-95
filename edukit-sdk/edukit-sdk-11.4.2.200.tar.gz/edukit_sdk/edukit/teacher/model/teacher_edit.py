#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
from edukit_sdk.edukit.teacher.model.teacher import Teacher


class TeacherEdit:
    def __init__(self):
        self._teacher_edit_id = None
        self._teacher = None

    @property
    def teacher_edit_id(self):
        """
        mixed
        :return:
        """
        return self._teacher_edit_id

    @teacher_edit_id.setter
    def teacher_edit_id(self, teacher_edit_id):
        """
        教师编辑版本ID
        :param teacher_edit_id:
        :return:
        """
        self._teacher_edit_id = teacher_edit_id

    @property
    def teacher(self):
        """
        mixed
        :return:
        """
        return self._teacher

    @teacher.setter
    def teacher(self, teacher: Teacher):
        """
        教师SDK请求体模型，详见Teacher类
        :param teacher:
        :return:
        """
        self._teacher = teacher
