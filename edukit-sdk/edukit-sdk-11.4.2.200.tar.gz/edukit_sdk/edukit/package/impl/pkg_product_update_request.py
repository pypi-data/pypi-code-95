#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.package.impl.pkg_handler import PkgHandler


class PkgProductUpdateRequest:
    def __init__(self, pkg_id, pkg_product_list, credential_list):
        self._pkg_id = pkg_id
        self._pkg_product_list = pkg_product_list
        self._pkg_handler = PkgHandler(EduKitRequestSender(credential_list))

    def update(self):
        return self._pkg_handler.update_pkg_product(self._pkg_id,
                                                    self._pkg_product_list)
