# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.course.model.course_edit_meta_data import \
    CourseEditMetaData


class CourseMetaData:
    """课程元数据类"""
    def __init__(self):
        self._meta_data = None
        self._country_codes = None

    @property
    def meta_data(self):
        """
        :return: mixed
        """
        return self._meta_data

    @meta_data.setter
    def meta_data(self, meta_data: CourseEditMetaData):
        """
        课程版本编辑元数据
        :param meta_data:
        :return:
        """
        self._meta_data = meta_data

    @property
    def country_codes(self):
        """
        :return: mixed
        """
        return self._country_codes

    @country_codes.setter
    def country_codes(self, country_codes):
        """
        * 课程可上架国家/地区列表，说明如下：
         * 将国家/地区加入此列表，表示允许教育中心在此国家/地区分发此课程
         * 此列表中必须包含中国大陆地区(代码为"CN")，其它国家/地区可选(当前教育中心业务仅覆盖中国大陆地区)
         * 首次提交后需要更新时，必须将更新后的可上架国家/地区列表全量提交，不能只提交变化的部分
         * 国家代码使用ISO-3166-1定义的两位字符形式代码，如中国为"CN"。代码需使用大写字符。
        :param country_codes:
        :return:
        """
        self._country_codes = country_codes

    def to_bytes(self):
        """
        将对象转为JSON类型的字节
        :return:bytes
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
