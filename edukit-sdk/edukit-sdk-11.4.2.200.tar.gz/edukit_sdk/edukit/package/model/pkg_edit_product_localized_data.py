#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class PkgEditProductLocalizedData:
    def __init__(self):
        self._language = None
        self._name = None

    @property
    def name(self):
        """
        :return:mixed
        """
        return self._name

    @property
    def language(self):
        """
        :return:mixed
        """
        return self._language

    @name.setter
    def name(self, name):
        """
        会员包名称
        最大30字符
        :param name:
        :return:
        """
        self._name = name

    @language.setter
    def language(self, language):
        """
        语言
        :param language:
        :return:
        """
        self._language = language