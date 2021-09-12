#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.package.impl.pkg_handler import PkgHandler


class PkgProductDeleteRequest:
    def __init__(self, pkg_id, pkg_edit_id, product_id, credential_list):
        self._pkg_id = pkg_id
        self._pkg_edit_id = pkg_edit_id
        self._product_id = product_id
        self._pkg_handler = PkgHandler(EduKitRequestSender(credential_list))

    def delete(self):
        return self._pkg_handler.delete(self._pkg_id, self._pkg_edit_id,
                                        self._product_id)
