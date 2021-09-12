# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.catalogue.impl.catalogue_handler import CatalogueHandler
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender


class CatalogueDeleteRequest:
    def __init__(self, course_id, course_edit_id, catalogue_id,
                 credential_list):
        self._course_id = course_id
        self._course_edit_id = course_edit_id
        self._catalogue_id = catalogue_id
        self._catalogue_handler = CatalogueHandler(
            EduKitRequestSender(credential_list))

    def delete(self):
        return self._catalogue_handler.delete_catalogue(
            self._course_id, self._course_edit_id, self._catalogue_id)
