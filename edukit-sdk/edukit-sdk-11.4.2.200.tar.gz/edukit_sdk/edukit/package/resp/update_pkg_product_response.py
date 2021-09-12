#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.model.response import Response


class UpdatePkgProductResponse(Response):
    def __init__(self):
        super(UpdatePkgProductResponse, self).__init__()
        self._details = None

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, details):
        self._details = details
