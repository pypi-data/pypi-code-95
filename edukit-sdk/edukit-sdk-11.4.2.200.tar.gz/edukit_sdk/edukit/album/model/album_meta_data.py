# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class AlbumMetaData:
    def __init__(self):
        self._recommend_flag = None
        self._is_combined_album = None
        self._name = None
        self._remarks = None

    @property
    def remarks(self):
        """
        :return:mixed
        """
        return self._remarks

    @remarks.setter
    def remarks(self, remarks):
        """
        提供给审核/运营人员查看的备注信息，不对最终用户呈现
        :param remarks:
        :return:1
        """
        self._remarks = remarks

    @property
    def recommend_flag(self):
        """
        :return:mixed
        """
        return self._recommend_flag

    @recommend_flag.setter
    def recommend_flag(self, recommend_flag):
        """
        专辑是否可推荐，为false时该专辑不在端侧展示
        :param recommend_flag:
        :return:
        """
        self._recommend_flag = recommend_flag

    @property
    def default_lang(self):
        """
        :return:mixed
        """
        return self._default_lang

    @default_lang.setter
    def default_lang(self, default_lang):
        """
        缺省语言
        :param default_lang:
        :return:
        """
        self._default_lang = default_lang

    @property
    def is_combined_album(self):
        """
        :return:mixed
        """
        return self._is_combined_album

    @is_combined_album.setter
    def is_combined_album(self, is_combined_album):
        """
        是否组合专辑，为true时只能关联子专辑，不能添加课程；为false时只能关联课程不能添加子专辑
        :param is_combined_album:
        :return:
        """
        self._is_combined_album = is_combined_album

    @property
    def name(self):
        """
        :return:mxied
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        专辑默认语言名称
        :param name:
        :return:
        """
        self._name = name