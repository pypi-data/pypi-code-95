# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class SubAlbum:
    def __init__(self):
        self._album_id = None
        self._oper_type = None
        self._order = None

    @property
    def album_id(self):
        """
        :return:mixed
        """
        return self._album_id

    @album_id.setter
    def album_id(self, album_id):
        """
        专辑ID
        :param album_id:
        :return:
        """
        self._album_id = album_id

    @property
    def order(self):
        """
        :return:mixed
        """
        return self._order

    @order.setter
    def order(self, order):
        """
        指定子专辑在专辑关联的列表里的位置，如果为1则该子专辑展示在归属的专辑中课程列表的第一位
        minimum:1 maximum:2000
        :param order:
        :return:
        """
        self._order = order

    @property
    def oper_type(self):
        """
        :return:mixed
        """
        return self._oper_type

    @oper_type.setter
    def oper_type(self, oper_type):
        """
        操作类型:
        minimum:1 maximum:3
        1-add，2-delete，3-modify
        :param oper_type:
        :return:
        """
        self._oper_type = oper_type