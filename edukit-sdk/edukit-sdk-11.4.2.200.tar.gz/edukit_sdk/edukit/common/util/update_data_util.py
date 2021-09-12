#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging

from edukit_sdk.edukit.common.constant.common_constant import CommonConstant
from edukit_sdk.edukit.common.constant.file_upload_constant import \
    FileUploadConstant
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.file_upload.file_upload import FileUpload
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.common.model.media_localized_data import \
    MediaLocalizedData
from edukit_sdk.edukit.common.model.update_media_localized_data import \
    UpdateMediaLocalizedData


class UpdateDataUtil:
    @staticmethod
    def update_multi_language_data(media_localized_data: MediaLocalizedData,
                                   request_sender: EduKitRequestSender):
        update_media_localized_data = UpdateMediaLocalizedData()
        update_media_localized_data.media_type \
            = media_localized_data.media_type
        update_media_localized_data.height = media_localized_data.height
        update_media_localized_data.width = media_localized_data.width
        update_media_localized_data.media_len = media_localized_data.media_len
        update_media_localized_data.ordinal = media_localized_data.ordinal

        upload_frame_img_result = UpdateDataUtil.upload_frame_image(
            media_localized_data, request_sender)

        if not upload_frame_img_result:
            return False

        if isinstance(upload_frame_img_result, str):
            update_media_localized_data.frame_id = upload_frame_img_result

        try:
            upload_media_result = UpdateDataUtil.upload_media(
                media_localized_data, request_sender)
        except EduKitException:
            return False

        if not upload_media_result:
            return False

        if isinstance(upload_media_result, dict):
            update_media_localized_data.meida_id = upload_media_result[
                'materialId']
            update_media_localized_data.file_name = Helpers.get_file_base_name(
                upload_media_result['path'])
            update_media_localized_data.size = Helpers.get_file_size(
                upload_media_result['path'])
            update_media_localized_data.sha256 = Helpers.get_sha256(
                upload_media_result['path'])

        return update_media_localized_data

    @staticmethod
    def upload_frame_image(media_localized_data: MediaLocalizedData,
                           request_sender: EduKitRequestSender):
        if not media_localized_data.frame_image_file_info:
            return True
        try:
            file_upload = FileUpload(
                path=media_localized_data.frame_image_file_info.path,
                resource_type=FileUploadConstant.
                RESOURCE_TYPE['PROMOTIONAL_VIDEO_POSTER'],
                request_sender=request_sender)
            result = file_upload.upload()
        except EduKitException as e:
            logging.error('Upload frame image failed. errMsg: {}'.format(
                str(e)))
            return False
        if not Helpers.is_success(result):
            logging.error('Upload frame image failed. errMsg: {}'.format(
                result['result']['resultDesc']))
            return False

        return result['materialId']

    @staticmethod
    def upload_media(media_localized_data: MediaLocalizedData,
                     request_sender: EduKitRequestSender):
        if not media_localized_data.media_file_info:
            return True
        public_file = False
        if media_localized_data.media_type == CommonConstant.MEDIA_TYPE[
                'COURSE_INTRODUCTION_VIDEO']:
            public_file = True
        try:
            file_upload = FileUpload(
                path=media_localized_data.media_file_info.path,
                file_type=media_localized_data.media_file_info.file_type,
                public_file=public_file,
                request_sender=request_sender)
            result = file_upload.upload()
        except EduKitException as e:
            logging.error('Upload media failed. errMsg: {}'.format(str(e)))
            return False

        if not Helpers.is_success(result):
            logging.error('Upload media failed. errMsg: {}'.format(
                result['result']['resultDesc']))
            return False

        return {
            'path': media_localized_data.media_file_info.path,
            'materialId': result['materialId']
        }
