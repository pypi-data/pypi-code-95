# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class LessonLocalizedData:
    def __init__(self):
        self._name = None
        self._deep_link_url = None

    @property
    def name(self):
        """
        :return:mixed
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        设置章节名称。
        对于每种已添加的语言类型，章节提交前必须指定此字段。后续更新时也要携带此字段。
        :param name:
        """
        self._name = name

    @property
    def deep_link_url(self):
        """
        :return:mixed
        """
        return self._deep_link_url

    @deep_link_url.setter
    def deep_link_url(self, deep_link_url):
        """
        设置从教育中心客户端跳转到您的APP的DeepLink链接。
        如果用户需要跳转到您的APP（eduappUsed=false）学习此章节，在章节首次提交前必须提供此链接。如课程支持在教育中心学习，则此字段为可选。
        章节版本更新时可不携带此字段，此时将保留当前值不变。
        提供此字段时，需要同时提供residentAGApp字段，以便能正确拉起您的APP。
        此链接仅用于学习章节内容时跳转，如果用户购买课程时需要跳转到您的APP，应设置课程元数据中的deepLink参数。
        可以在此链接中增加必要的参数以辅助跳转后在您的APP内的逻辑处理，教育中心将透传这些参数。但请勿在链接中携带敏感数据（如用户密码等）。
        :param deep_link_url:
        """
        self._deep_link_url = deep_link_url

    def to_bytes(self):
        """
        将对象转为JSON类型的字节
        :return:bytes
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)), 'utf-8')
