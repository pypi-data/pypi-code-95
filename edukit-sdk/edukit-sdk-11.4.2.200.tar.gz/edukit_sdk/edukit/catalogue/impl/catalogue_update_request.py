# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.catalogue.impl.catalogue_handler import CatalogueHandler
from edukit_sdk.edukit.catalogue.model.catalogue import Catalogue
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender


class CatalogueUpdateRequest:
    def __init__(self, catalogue: Catalogue, course_id, course_edit_id,
                 credential_list):
        self._catalogue = catalogue
        self._course_id = course_id
        self._course_edit_id = course_edit_id
        self._catalogue_handler = CatalogueHandler(
            EduKitRequestSender(credential_list))

    def update(self):
        return self._catalogue_handler.update_catalogue(
            self._catalogue, self._course_id, self._course_edit_id)
