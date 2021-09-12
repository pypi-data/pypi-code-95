# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class CatalogueFullLocalizedData:
    def __init__(self):
        self._name = None
        self._language = None

    @property
    def name(self):
        """
        :return: mixed
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        目录名称
        :param name:
        :return:
        """
        self._name = name

    @property
    def language(self):
        """
        :return: mixed
        """
        return self._language

    @language.setter
    def language(self, language):
        """
        语言代码
        :param language:
        :return:
        """
        self._language = language
