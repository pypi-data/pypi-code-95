# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class LessonMultiLanguageData:
    def __init__(self):
        self._language = None
        self._lesson_localized_data = None
        self._media_localized_data = None

    @property
    def language(self):
        """
        :return:mixed
        """
        return self._language

    @language.setter
    def language(self, language):
        """
        设置章节语言信息。
        语言代码由BCP-47定义，如简体中文为"zh-CN"，区分大小写（语言标识使用小写字母；区域名称使用大写字母）。
        :param language:
        """
        self._language = language

    @property
    def lesson_localized_data(self):
        """
        :return:mixed
        """
        return self._lesson_localized_data

    @lesson_localized_data.setter
    def lesson_localized_data(self, lesson_localized_data):
        """
        设置章节本地化多语言数据。
        :param lesson_localized_data:
        """
        self._lesson_localized_data = lesson_localized_data

    @property
    def media_localized_data(self):
        """
        :return:mixed
        """
        return self._media_localized_data

    @media_localized_data.setter
    def media_localized_data(self, media_localized_data):
        """
        设置章节媒体文件。
        :param media_localized_data:
        """
        self._media_localized_data = media_localized_data
