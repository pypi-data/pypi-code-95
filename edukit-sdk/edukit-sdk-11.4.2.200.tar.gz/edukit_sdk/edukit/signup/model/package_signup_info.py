# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class PackageSignupInfo:
    def __init__(self):
        self._package_id = None
        self._product_no = None
        self._signup_info = None

    @property
    def package_id(self):
        """
        :return:
        """
        return self._package_id

    @package_id.setter
    def package_id(self, package_id):
        """
        设置会员包ID。
        教育中心分配的会员包ID，通过getPkgId()接口获取。
        :param package_id:
        :return:
        """
        self._package_id = package_id

    @property
    def product_no(self):
        """
        :return:
        """
        return self._product_no

    @product_no.setter
    def product_no(self, product_no):
        """
        由您分配的商品ID，需要与创建会员包商品时指定的devProductId相同。
        :param product_no:
        :return:
        """
        self._product_no = product_no

    @property
    def signup_info(self):
        """
        mixed
        :return:
        """
        return self._signup_info

    @signup_info.setter
    def signup_info(self, signup_info):
        """
        设置订购关系信息
        :param signup_info:
        :return:
        """
        self._signup_info = signup_info

    def to_json_string(self):
        """
        to_string
        :return:
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
