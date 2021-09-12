# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class SeriesCourseLearningInfo:
    def __init__(self):
        self._start_time = None
        self._course_learning_status = None
        self._lesson_learning_status = None

    @property
    def start_time(self):
        """
        :return:mixed
        """
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        """
        设置本次学习开始时间。
        使用RFC3339定义的UTC时间格式(即GMT+00时区的时间)，例：2021-12-20T08:00:00Z。
        :param start_time:
        :return:
        """
        self._start_time = start_time

    @property
    def course_learning_status(self):
        """
        :return:mixed
        """
        return self._course_learning_status

    @course_learning_status.setter
    def course_learning_status(self, course_learning_status):
        """
        设置本次学习结束后，课程整体学习完成状态，1表示正在学，2表示已学完。
        如上报的学习状态为2，则该课程将标记为"学习完成"状态。上报课程整体状态为已学完不要求课程下所有章节的状态都为已学完。
        如未上报课程整体学习状态，教育中心将根据上报的章节状态自动计算课程整体的学习状态，计算方式为“课程下所有章节已学完则课程学习状态为已学完”。

        :param course_learning_status:
        :return:
        """
        self._course_learning_status = course_learning_status

    @property
    def lesson_learning_status(self):
        """
        :return:mixed
        """
        return self._lesson_learning_status

    @lesson_learning_status.setter
    def lesson_learning_status(self, lesson_learning_status):
        """
        设置本次学习结束后，章节学习完成状态。
        1-正在学，表示用户已经开始学习该章节但是尚未完成；2-已学完，表示用户已经完成该章节的学习。
        :param lesson_learning_status:
        :return:
        """
        self._lesson_learning_status = lesson_learning_status

    def to_json_string(self):
        """
        将对象转为JSON字符串
        :return:
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
