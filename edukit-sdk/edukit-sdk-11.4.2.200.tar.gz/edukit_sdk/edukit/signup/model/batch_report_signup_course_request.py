# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class BatchReportSignupCourseRequest:
    def __init__(self):
        self._status = None
        self._signup_list = None

    @property
    def status(self):
        """
        :return:
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        设置课程订购状态
        :param status: 2：已订购,4：已退订
        :return:
        """
        self._status = status

    @property
    def signup_list(self):
        """
        :return:
        """
        return self._signup_list

    @signup_list.setter
    def signup_list(self, signup_list):
        """
        设置多订单课程订购记录
        :param signup_list:
        :return:
        """
        self._signup_list = signup_list

    def to_json_string(self):
        """
        to_string
        :return:
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
