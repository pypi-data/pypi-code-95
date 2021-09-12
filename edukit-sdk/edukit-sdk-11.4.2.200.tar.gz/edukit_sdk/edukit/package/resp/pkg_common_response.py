#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.model.response import Response


class PkgCommonResponse(Response):
    def __init__(self):
        super(PkgCommonResponse, self).__init__()
        self._pkg_id = None
        self._pkg_edit_id = None

    @property
    def pkg_id(self):
        return self._pkg_id

    @pkg_id.setter
    def pkg_id(self, pkg_id):
        self._pkg_id = pkg_id

    @property
    def pkg_edit_id(self):
        return self._pkg_edit_id

    @pkg_edit_id.setter
    def pkg_edit_id(self, pkg_edit_id):
        self._pkg_edit_id = pkg_edit_id
