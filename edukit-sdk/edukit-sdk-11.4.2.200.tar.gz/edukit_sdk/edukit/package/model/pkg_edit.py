#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class PkgEdit:
    def __init__(self):
        self._meta_data = None
        self._localized_data = None
        self._pkg_products = None

    @property
    def meta_data(self):
        """
        :return:mixed
        """
        return self._meta_data

    @meta_data.setter
    def meta_data(self, meta_data):
        """
        会员包版本元数据
        :param meta_data:
        :return:
        """
        self._meta_data = meta_data

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
    def pkg_products(self):
        """
        :return:mixed
        """
        return self._pkg_products

    @pkg_products.setter
    def pkg_products(self, pkg_products):
        """
        商品列表信息，最大100个
        :param pkg_products:
        :return:
        """
        self._pkg_products = pkg_products
