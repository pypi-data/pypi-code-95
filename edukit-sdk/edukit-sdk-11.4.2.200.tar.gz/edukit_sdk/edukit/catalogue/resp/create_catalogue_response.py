# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.model.response import Response


class CreateCatalogueResponse(Response):
    def __init__(self):
        self._catalogue_id = None
        self._catalogue_edit_id = None
        super(CreateCatalogueResponse, self).__init__()

    @property
    def catalogue_id(self):
        return self._catalogue_id

    @catalogue_id.setter
    def catalogue_id(self, catalogue_id):
        self._catalogue_id = catalogue_id

    @property
    def catalogue_edit_id(self):
        return self._catalogue_edit_id

    @catalogue_edit_id.setter
    def catalogue_edit_id(self, catalogue_edit_id):
        self._catalogue_edit_id = catalogue_edit_id
