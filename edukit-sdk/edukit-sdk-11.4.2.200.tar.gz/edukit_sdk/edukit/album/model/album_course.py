# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class AlbumCourse:
    def __init__(self):
        self._content_id = None
        self._oper_type = None
        self._order = None

    @property
    def content_id(self):
        """
        :return:mixed
        """
        return self._content_id

    @content_id.setter
    def content_id(self, content_id):
        """
        内容ID
        :param content_id:
        """
        self._content_id = content_id

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
        """
        self._oper_type = oper_type

    @property
    def order(self):
        """
        :return:mixed
        """
        return self._order

    @order.setter
    def order(self, order):
        """
        指定课程在专辑关联的列表里的位置，如果为1则该课程展示在归属的专辑中课程列表的第一位
        minimum:1 maximum:2000
        :param order:
        """
        self._order = order
