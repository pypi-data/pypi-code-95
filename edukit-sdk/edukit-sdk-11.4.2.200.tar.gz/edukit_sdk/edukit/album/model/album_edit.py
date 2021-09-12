# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class AlbumEdit:
    def __init__(self):
        self._meta_data = None
        self._localized_data = None
        self._course_list = None
        self._sub_album_list = None

    @property
    def localized_data(self):
        """
        :return:mixed
        """
        return self._localized_data

    @localized_data.setter
    def localized_data(self, localized_data):
        """
        本地化多语言数据
        :param localized_data:
        :return:
        """
        self._localized_data = localized_data

    @property
    def meta_data(self):
        """
        :return:mixed
        """
        return self._meta_data

    @meta_data.setter
    def meta_data(self, meta_data):
        """
        版本元数据
        :param mete_data:
        :return:
        """
        self._meta_data = meta_data

    @property
    def course_list(self):
        """
        :return:mixed
        """
        return self._course_list

    @course_list.setter
    def course_list(self, course_list):
        """
        课程ID列表信息，最大2000个
        :param course_list:
        :return:
        """
        self._course_list = course_list

    @property
    def sub_album_list(self):
        """
        :return:mixed
        """
        return self._sub_album_list

    @sub_album_list.setter
    def sub_album_list(self, sub_album_list):
        """
        专辑ID列表信息，最大20个
        :param sub_album_list:
        :return:
        """
        self._sub_album_list = sub_album_list

    def to_json_string(self):
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
