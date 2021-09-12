#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.package.impl.pkg_handler import PkgHandler


class PkgCreateRequest:
    def __init__(self, pkg, credential_list):
        self._pkg = pkg
        self._pkg_handler = PkgHandler(EduKitRequestSender(credential_list))

    def create(self):
        self._pkg_handler.covert_localized_datas(self._pkg)
        return self._pkg_handler.create_pkg(self._pkg)
