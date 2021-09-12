# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.model.response import Response


class UpdateCatalogueResponse(Response):
    def __init__(self):
        self._catalogue_edit_id = None
        super(UpdateCatalogueResponse, self).__init__()

    @property
    def catalogue_edit_id(self):
        return self._catalogue_edit_id

    @catalogue_edit_id.setter
    def catalogue_edit_id(self, catalogue_edit_id):
        self._catalogue_edit_id = catalogue_edit_id
