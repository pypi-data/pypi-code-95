# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class CourseMultiLanguageData:
    def __init__(self):
        self._language = None
        self._course_localized_data = None
        self._media_localized_data_list = None

    @property
    def language(self):
        """
        :return: mixed
        """
        return self._language

    @language.setter
    def language(self, language):
        """
        多语言信息
        :param language:
        :return:
        """
        self._language = language

    @property
    def course_localized_data(self):
        """
        :return: mixed
        """
        return self._course_localized_data

    @course_localized_data.setter
    def course_localized_data(self, course_localized_data):
        """
        课程本地化多语言数据对象
        :param course_localized_data:
        :return:
        """
        self._course_localized_data = course_localized_data

    @property
    def media_localized_data_list(self):
        """
        :return: mixed
        """
        return self._media_localized_data_list

    @media_localized_data_list.setter
    def media_localized_data_list(self, media_localized_data_list):
        """
        媒体文件列表
        :param media_localized_data_list:
        :return:
        """
        self._media_localized_data_list = media_localized_data_list
