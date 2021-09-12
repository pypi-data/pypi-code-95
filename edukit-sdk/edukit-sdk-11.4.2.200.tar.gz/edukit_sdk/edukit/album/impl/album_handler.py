# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json
import logging
import os

from edukit_sdk.edukit.album.model.localized_data import LocalizedData
from edukit_sdk.edukit.album.resp.create_album_response import \
    CreateAlbumResponse
from edukit_sdk.edukit.album.resp.update_album_response import \
    UpdateAlbumResponse
from edukit_sdk.edukit.common.constant.api_constant import ApiConstant
from edukit_sdk.edukit.common.constant.file_upload_constant import \
    FileUploadConstant
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.file_upload.file_upload import FileUpload
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.http_common_response import \
    HttpCommonResponse


class AlbumHandler:
    __img_type_list = {
        FileUploadConstant.RESOURCE_TYPE['COURSE_PACKAGE_HORIZONTAL_COVER']:
        'cover image',
        FileUploadConstant.RESOURCE_TYPE['ALBUM_LANDSCAPE_COVER']:
        'landscape cover image'
    }

    def __init__(self, request_sender):
        self.__request_sender = request_sender

    def create_album(self, album):
        logging.info('Call create_album interface start.')
        create_album_response = CreateAlbumResponse()
        try:
            url = ApiConstant.CREATE_ALBUM_URL
            body = album.to_json_string()
            response = HttpCommonResponse(
                self.__request_sender.post(url=url, body=body))
            create_album_response = Helpers.parse_response(
                response.get_rsp(),
                'edukit_sdk.edukit.album.resp.create_album_response'
                '.CreateAlbumResponse'
            )
        except EduKitException as e:
            logging.error('Call createAlbum interface failed.error_message:' +
                          str(e))
            create_album_response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)

        logging.info(
            'Call create_album interface end, and albumId: %s, albumEditId: %s'
            % (create_album_response.album_id, create_album_response.edit_id))

        return create_album_response

    def update_album(self, album_id, album):
        logging.info('Call update_album interface start.')
        update_album_response = UpdateAlbumResponse()
        try:
            url = ApiConstant.CREATE_UPDATE_ALBUM_URL.format(album_id)
            body = album.to_json_string()
            response = HttpCommonResponse(
                self.__request_sender.put(url=url, body=body))
            update_album_response = Helpers.parse_response(
                response.get_rsp(),
                'edukit_sdk.edukit.album.resp.update_album_response'
                '.UpdateAlbumResponse'
            )
        except EduKitException as e:
            logging.error('Call update_album interface failed.error_message:' +
                          str(e))
            update_album_response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)

        logging.info(
            'Call update_album interface end, and albumId: %s, albumEditId: %s'
            % (update_album_response.album_id, update_album_response.edit_id))

        return update_album_response

    def manage_album(self, album_id, action, removal_reason):
        logging.info('Call manage_album interface start.')
        try:
            url = ApiConstant.MANAGE_ALBUM_STATUS_URL.format(album_id)
            body = {"action": action, "removalReason": removal_reason}
            by = bytes(json.dumps(body), encoding='utf-8')
            response = HttpCommonResponse(
                self.__request_sender.post(url=url, body=by))
            logging.info('Call manage_album interface end. albumId: ' +
                         str(album_id))
            return Helpers.build_result(response.get_rsp())
        except EduKitException as e:
            logging.error(
                'Call manage_album interface failed. error_message: ' + str(e))
            return Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)

    def delete_album(self, album_id):
        logging.info('Call delete_album interface start.')
        try:
            url = ApiConstant.DELETE_ALBUM_URL.format(album_id)
            response = HttpCommonResponse(
                self.__request_sender.delete(url=url))
            logging.info('Call delete_album interface end. albumId: ' +
                         str(album_id))
            return Helpers.build_result(response.get_rsp())
        except EduKitException as e:
            logging.error(
                'Call delete_album interface failed. error_message:' + str(e))
            return Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)

    def format_data(self, album):
        if not album.edit or not album.edit.localized_data:
            return album
        edit_localized_data_list = list()
        for item in album.edit.localized_data:
            edit_localized_data = LocalizedData()
            edit_localized_data.language = item.language
            edit_localized_data.name = item.name
            edit_localized_data.full_description = item.full_description

            if item.cover_img_file_info:
                upload_cover_img_result = self.upload_img(
                    item.cover_img_file_info)
                if not upload_cover_img_result:
                    return False
                if isinstance(upload_cover_img_result, str):
                    edit_localized_data.cover_img_id = upload_cover_img_result
            if item.landscape_cover_img_file_info:
                upload_landscape_img_result = self.upload_img(
                    item.landscape_cover_img_file_info)
                if not upload_landscape_img_result:
                    return False
                if isinstance(upload_landscape_img_result, str):
                    edit_localized_data.landscape_cover_img_id = \
                        upload_landscape_img_result

            edit_localized_data_list.append(edit_localized_data)

        album.edit.localized_data = edit_localized_data_list
        return album

    def upload_img(self, image_file_info):
        img_type = self.__img_type_list[image_file_info.resource_type]
        try:
            file_upload = FileUpload(
                path=image_file_info.path,
                resource_type=image_file_info.resource_type,
                request_sender=self.__request_sender)
            result = file_upload.upload()
        except EduKitException as e:
            logging.error("Upload %s failed. errMsg:%s" % (img_type, str(e)))
            return FileUpload
        if not Helpers.is_success(result):
            logging.error("Upload %s failed. errMsg:%s" %
                          (img_type, result['result']['resultDesc']))

        return result['materialId']
