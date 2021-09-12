# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class CatalogueFullMetaData:
    def __init__(self):
        self._name = None
        self._default_lang = None
        self._parent_id = None
        self._display_order = None
        self._create_time = None
        self._last_update = None

    @property
    def parent_id(self):
        """
        :return: mixed
        """
        return self._parent_id

    @parent_id.setter
    def parent_id(self, parent_id):
        """
        父目录ID，创建子目录时携带，不携带时，默认创建一级目录
        :param parent_id:
        :return:
        """
        self._parent_id = parent_id

    @property
    def display_order(self):
        """
        :return: mixed
        """
        return self._display_order

    @display_order.setter
    def display_order(self, display_order):
        """
        同一课程目录列表中该目录的排列顺序
        :param display_order:
        :return:
        """
        self._display_order = display_order

    @property
    def default_lang(self):
        """
        :return: mixed
        """
        return self._default_lang

    @default_lang.setter
    def default_lang(self, default_lang):
        """
        目录的默认语言代码
        :param default_lang:
        :return:
        """
        self._default_lang = default_lang

    @property
    def create_time(self):
        """
        :return: mixed
        """
        return self._create_time

    @create_time.setter
    def create_time(self, create_time):
        """
        目录创建时间，order相同时，按创建时间从早到晚排序， 使用RFC3339定义的UTC时间格式
        :param create_time:
        :return:
        """
        self._create_time = create_time

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
    def last_update(self):
        """
        :return: mixed
        """
        return self._last_update

    @last_update.setter
    def last_update(self, last_update):
        """
        目录版本更新时间，使用RFC3339定义的UTC时间格式
        :param last_update:
        :return:
        """
        self._last_update = last_update
