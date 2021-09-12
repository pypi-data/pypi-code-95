# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class UpdateProductPriceRequest:
    def __init__(self):
        self._product_prices = None

    @property
    def product_prices(self):
        return self._product_prices

    @product_prices.setter
    def product_prices(self, product_prices):
        self._product_prices = product_prices

    def to_bytes(self):
        """
        将对象转为JSON类型的字节
        :return:bytes
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)), 'utf-8')
