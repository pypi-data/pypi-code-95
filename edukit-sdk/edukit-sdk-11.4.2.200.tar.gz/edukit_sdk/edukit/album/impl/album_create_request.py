# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.album.impl.album_handler import AlbumHandler
from edukit_sdk.edukit.album.resp.create_album_response import \
    CreateAlbumResponse
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender


class AlbumCreateRequest:
    def __init__(self, album, credential_list):
        self.__album = album
        self.__album_handler = AlbumHandler(
            EduKitRequestSender(credential_list))

    def create(self):
        formatted_album = self.__album_handler.format_data(self.__album)
        if not formatted_album:
            create_album_response = CreateAlbumResponse()
            create_album_response.result = Helpers.build_error_result(
                    CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return create_album_response
        return self.__album_handler.create_album(formatted_album)
