#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class Products:
    def __init__(self):
        self._products = None

    @property
    def products(self):
        """
        :return: mixed
        """
        return self._products

    @products.setter
    def products(self, products):
        """
        商品列表信息
        :param products:
        :return:
        """
        self._products = products

    def to_json_string(self):
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
