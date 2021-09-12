#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.package.impl.pkg_handler import PkgHandler


class PkgManageRequest:
    def __init__(self, pkg_id, action, removal_reason, credential_list):
        self._pkg_id = pkg_id
        self._action = action
        self._removal_reason = removal_reason
        self._pkg_handler = PkgHandler(EduKitRequestSender(credential_list))

    def manage(self):
        return self._pkg_handler.manage(self._pkg_id, self._action,
                                        self._removal_reason)
