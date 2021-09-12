# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class UnitaryCourseLearningInfo:
    def __init__(self):
        self._start_time = None
        self._learning_status = None

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
    def learning_status(self):
        """
        :return:mixed
        """
        return self._learning_status

    @learning_status.setter
    def learning_status(self, learning_status):
        """

        :param learning_status:
        :return:
        """
        self._learning_status = learning_status

    def to_json_string(self):
        """
        将对象转为JSON字符串
        :return:
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
