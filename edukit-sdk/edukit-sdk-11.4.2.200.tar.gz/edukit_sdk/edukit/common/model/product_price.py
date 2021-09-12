#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class ProductPrice:
    def __init__(self):
        self._country_code = None
        self._price_type = None
        self._price = None

    @property
    def country_code(self):
        return self._country_code

    """
     * 价格对应的国家/地区代码。
     * 使用[ISO-3166-1]定义的两位字符形式的国家代码。如中国为"CN"。
     * 国家代码需要使用大写字符形式。
     * 最大长度 : 10
     * 示例: "CN"
     * :param: mixed country_code
     * :return: ProductPrice
    """

    @country_code.setter
    def country_code(self, country_code):
        self._country_code = country_code

    @property
    def price_type(self):
        return self._price_type

    """
     * 价格类型， 支持原始价格和售卖价格两种类型：
     * 1: 原始价格。可用在降价促销等场景展示商品原始价格；教育中心App显示原价时，将使用删除线进行标识。
     * 2: 售卖价格。用户购买商品时实际需要支付的价格。
     * 说明：
     * 原始价格为可选字段，如不指定则只展示售卖价格。
     * 售卖价格必须小于原始价格，否则将返回错误。
     * :param: mixed price_type
     * :return: ProductPrice
    """

    @price_type.setter
    def price_type(self, price_type):
        self._price_type = price_type

    @property
    def price(self):
        return self._price

    """
     * 商品价格。
     * 价格对应的货币单位由countryCode代表的国家确定。每个国家默认的货币单位可联系华为运营人员获取。
     * 价格单位为基准货币单位(即"元")。
     * 价格最多支持19位数字(包含小数部分)，最多支持2位小数。
     * 部分货币类型只支持整数，不支持小数。具体可参考[ISO-4217]exponent部分为0的货币。
     * 示例: 99.9
     * :param: mixed price
     * :return: ProductPrice
    """

    @price.setter
    def price(self, price):
        self._price = price
