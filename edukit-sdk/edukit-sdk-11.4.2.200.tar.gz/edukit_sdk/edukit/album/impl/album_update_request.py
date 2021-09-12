# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.album.impl.album_handler import AlbumHandler
from edukit_sdk.edukit.album.resp.update_album_response import \
    UpdateAlbumResponse
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender


class AlbumUpdateRequest:
    def __init__(self, album_id, album, credential_list):
        self.__album_id = album_id
        self.__album = album
        self.__album_handler = AlbumHandler(
            EduKitRequestSender(credential_list))

    def update(self):
        formatted_album = self.__album_handler.format_data(self.__album)
        if not formatted_album:
            update_album_response = UpdateAlbumResponse()
            update_album_response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return update_album_response
        return self.__album_handler.update_album(self.__album_id,
                                                 formatted_album)
