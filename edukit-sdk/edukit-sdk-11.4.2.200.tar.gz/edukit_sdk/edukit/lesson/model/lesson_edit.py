# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class LessonEdit:
    def __init__(self):
        self._course_id = None
        self._course_edit_id = None
        self._lesson_edit_id = None
        self._lesson = None

    @property
    def course_id(self):
        """
        :return:mixed
        """
        return self._course_id

    @course_id.setter
    def course_id(self, course_id):
        """
        设置课程ID。创建课程时返回，通过getCourseId()获取。
        :param course_id:
        """
        self._course_id = course_id

    @property
    def course_edit_id(self):
        """
        :return:mixed
        """
        return self._course_edit_id

    @course_edit_id.setter
    def course_edit_id(self, course_edit_id):
        """
        设置课程版本ID。创建或更新课程时返回，也可用通过createNewEdit()创建新的课程编辑版本。
        :param course_edit_id:
        """
        self._course_edit_id = course_edit_id

    @property
    def lesson_edit_id(self):
        """
        :return:mixed
        """
        return self._lesson_edit_id

    @lesson_edit_id.setter
    def lesson_edit_id(self, lesson_edit_id):
        """
        设置章节版本ID，用于标识课程章节的一个版本，每次对章节进行更新时都需要生成一个新的版本ID。
        章节版本ID通过createLesson接口(首次创建章节时)或updateLesson接口(后续更新章节时)获得。
        :param lesson_edit_id:
        """
        self._lesson_edit_id = lesson_edit_id

    @property
    def lesson(self):
        """
        :return:mixed
        """
        return self._lesson

    @lesson.setter
    def lesson(self, lesson):
        """
        设置章节数据。
        :param lesson:
        """
        self._lesson = lesson
