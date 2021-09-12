# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class OrderInfo:
    def __init__(self):
        self._order_id = None
        self._order_time = None
        self._pay_order_id = None

    @property
    def order_id(self):
        """
        :return: order_id
        """
        return self._order_id

    @order_id.setter
    def order_id(self, order_id):
        """
        设置用户购买课程/会员包时，华为应用内支付服务生成的订单ID。
        对于教育中心直购的场景，应从商品发货通知接口中的order_id字段获取订单号上报。
        对于在您的APP中直接产生的课程/会员包购买，应上报HMS应用内支付服务返回的order_id。
        如果您接入应用内支付V2.0，可以通过支付成功后客户端回调接口中的PayResultInfo对象，或者服务端回调接口中获得order_id。
        如果您接入应用内支付V3.0及以上版本，可以通过支付成功后onActivityResult返回的InAppPurchaseData对象获得order_id。
        对于用户续订时产生的订购关系同步，应上报续订操作行为对应的order_id。
        :param order_id:
        :return:
        """
        self._order_id = order_id

    @property
    def order_time(self):
        """
        :return:
        """
        return self._order_time

    @order_time.setter
    def order_time(self, order_time):
        """
        订单完成的时间，使用RFC3339定义的UTC时间格式(即GMT+00时区的时间)。
        :param order_time:
        :return:
        """
        self._order_time = order_time

    @property
    def pay_order_id(self):
        """
        :return:
        """
        return self._pay_order_id

    @pay_order_id.setter
    def pay_order_id(self, pay_order_id):
        """
        设置用户购买课程/会员包时，华为支付平台生成的订单ID。
        仅当用户直接在您的APP中购买课程/会员包，且您接入华为应用内支付V3.0服务时，才需要上报此字段。
        您可以通过支付成功后onActivityResult返回的InAppPurchaseData对象获得pay_order_id。
        对于用户续订时产生的订购关系同步，应上报续订操作行为对应的pay_order_id。
        :param pay_order_id:
        :return:
        """
        self._pay_order_id = pay_order_id

    def to_json_string(self):
        """
        to_string
        :return:
        """
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
