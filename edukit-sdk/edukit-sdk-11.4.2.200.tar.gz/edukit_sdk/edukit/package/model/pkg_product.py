#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class PkgProduct:
    def __init__(self):
        self._name = None
        self._default_lang = None
        self._dev_product_id = None
        self._status = None
        self._localized_data = None
        self._validity_unit = None
        self._validity_num = None
        self._deeplink_url = None
        self._need_delivery = None
        self._price_list = None

    @property
    def name(self):
        """
        :return: mixed
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        会员包关联商品名称
        :param name:
        :return:
        """
        self._name = name

    @property
    def default_lang(self):
        """
        缺省语言
        :return:
        """
        return self._default_lang

    @default_lang.setter
    def default_lang(self, default_lang):
        self._default_lang = default_lang

    @property
    def dev_product_id(self):
        """
        :return: mixed
        """
        return self._dev_product_id

    @dev_product_id.setter
    def dev_product_id(self, dev_product_id):
        """
        会员包关联商品ID
        :param dev_product_id:
        :return:
        """
        self._dev_product_id = dev_product_id

    @property
    def localized_data(self):
        """
        :return: mixed
        """
        return self._localized_data

    @localized_data.setter
    def localized_data(self, localized_data):
        """
        会员包版本商品本地化多语言数据，即需要随会员包版本进行审核的商品本地化多语言数据
        :param localized_data:
        :return:
        """
        self._localized_data = localized_data

    @property
    def validity_unit(self):
        """
        :return: mixed
        """
        return self._validity_unit

    @validity_unit.setter
    def validity_unit(self, validity_unit):
        """
        会员包订购关系有效期长度单位
        :param validity_unit:
        :return:
        """
        self._validity_unit = validity_unit

    @property
    def status(self):
        """
        :return: mixed
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        会员包商品状态
        :param status:
        :return:
        """
        self._status = status

    @property
    def validity_num(self):
        """
        :return: mixed
        """
        return self._validity_num

    @validity_num.setter
    def validity_num(self, validity_num):
        """
        会员包订购关系有效期长度
        :param validity_num:
        :return:
        """
        self._validity_num = validity_num

    @property
    def deeplink_url(self):
        """
        :return: mixed
        """
        return self._deeplink_url

    @deeplink_url.setter
    def deeplink_url(self, deeplink_url):
        """
        从教育中心App跳转到您的App的DeepLink链接
        :param deeplink_url:
        :return:
        """
        self._deeplink_url = deeplink_url

    @property
    def need_delivery(self):
        """
        :return: mixed
        """
        return self._need_delivery

    @need_delivery.setter
    def need_delivery(self, need_delivery):
        """
        商品购买后是否需要邮寄材料
        :param need_delivery:
        :return:
        """
        self._need_delivery = need_delivery

    @property
    def price_list(self):
        """
        :return:mixed
        """
        return self._price_list

    @price_list.setter
    def price_list(self, price_list):
        """
        多个国家的会员包商品定价
        :param price_list:
        :return:
        """
        self._price_list = price_list
