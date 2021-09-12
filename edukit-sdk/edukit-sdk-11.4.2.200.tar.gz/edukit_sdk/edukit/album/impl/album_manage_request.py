# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.album.impl.album_handler import AlbumHandler
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender


class AlbumManageRequest:
    def __init__(self, album_id, action, removal_reason, credential_list):
        self.__album_id = album_id
        self.__action = action
        self.__removal_reason = removal_reason
        self.__album_handler = AlbumHandler(
            EduKitRequestSender(credential_list))

    def manage(self):
        return self.__album_handler.manage_album(self.__album_id,
                                                 self.__action,
                                                 self.__removal_reason)
