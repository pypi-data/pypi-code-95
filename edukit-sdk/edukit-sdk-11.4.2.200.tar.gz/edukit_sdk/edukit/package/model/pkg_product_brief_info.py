#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class PkgProductBriefInfo:
    def __init__(self):
        self._dev_product_id = None
        self._status = None
        self._price_list = None

    @property
    def dev_product_id(self):
        """
        :return: mixed
        """
        return self._dev_product_id

    @dev_product_id.setter
    def dev_product_id(self, dev_product_id):
        """
        商品ID,开发者指定，创建时必填，建议开发者在devProductId前拼上CP公司缩写或者其他可以保证全局唯一的标识
        :param dev_product_id:
        :return:
        """
        self._dev_product_id = dev_product_id

    @property
    def status(self):
        """
        :return: mixed
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        会员包商品状态，0-停售会员包商品，1-激活会员包商品
        :param status:
        :return:
        """
        self._status = status

    @property
    def price_list(self):
        """
        :return: mixed
        """
        return self._price_list

    @price_list.setter
    def price_list(self, price_list):
        """
        多国家定价数据，至少1个，更新时全量提交
        :param price_list:
        :return:
        """
        self._price_list = price_list
