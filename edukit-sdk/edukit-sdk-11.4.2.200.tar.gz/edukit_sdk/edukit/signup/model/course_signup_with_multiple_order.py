# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class CourseSignupWithMultipleOrder:
    def __init__(self):
        self._course_id = None
        self._expire = None
        self._orders = None

    @property
    def course_id(self):
        """
        :return:
        """
        return self._course_id

    @course_id.setter
    def course_id(self, course_id):
        """
        设置用户订购/退订的课程ID。
        :param course_id:
        :return:
        """
        self._course_id = course_id

    @property
    def expire(self):
        """
        :return:
        """
        return self._expire

    @expire.setter
    def expire(self, expire):
        """
        设置订购关系的失效时间。
        订购状态为“2：已订购”时，您可以通过此字段显式指定订购关系的失效时间。
        超过此时间的后用户不可再使用此课程/会员包。
        该字段可选。如果您不指定此字段，将根据订购时间以及您创建课程时设置的订购关系有效期(validityNum)自动计算失效时间。
        :param expire:
        :return:
        """
        self._expire = expire

    @property
    def orders(self):
        """
        :return:
        """
        return self._orders

    @orders.setter
    def orders(self, orders):
        """
        设置该订购记录对应的订单列表。
        如果一次课程购买对应了多笔支付订单（如定金+尾款场景），可一次性传递所有订单。
        :param orders:
        :return:
        """
        self._orders = orders

    def to_json_string(self):
        """
        to_string
        :return:
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
