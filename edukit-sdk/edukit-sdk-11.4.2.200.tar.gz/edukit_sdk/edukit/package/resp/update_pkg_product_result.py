#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.model.response import Response


class UpdatePkgProductResult(Response):
    def __init__(self):
        super(UpdatePkgProductResult, self).__init__()
        self._dev_product_id = None

    @property
    def dev_product_id(self):
        return self._dev_product_id

    @dev_product_id.setter
    def dev_product_id(self, dev_product_id):
        self._dev_product_id = dev_product_id
