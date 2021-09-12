# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class CourseEdit:
    """课程版本操作请求体"""
    def __init__(self):
        self._course_edit_id = None
        self._course = None

    @property
    def course_edit_id(self):
        """
        :return: mixed
        """
        return self._course_edit_id

    @course_edit_id.setter
    def course_edit_id(self, course_edit_id):
        """
        课程编辑版本ID
        :param course_edit_id:
        :return:
        """
        self._course_edit_id = course_edit_id

    @property
    def course(self):
        """
        :return: mixed
        """
        return self._course

    @course.setter
    def course(self, course):
        """
        课程模型
        :param course:
        :return:
        """
        self._course = course
