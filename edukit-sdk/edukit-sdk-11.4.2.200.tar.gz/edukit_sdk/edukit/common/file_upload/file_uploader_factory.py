#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.file_upload.upload_media import UploadMedia
from edukit_sdk.edukit.common.file_upload.upload_picture import UploadPicture


class FileUploaderFactory:
    def __init__(self, file_request, request_sender):
        self._file_request = file_request
        self._request_sender = request_sender

    def get_file_uploader(self, resource_type=None):
        # 传入resource_type,使用图片上传
        if resource_type:
            return UploadPicture(self._file_request, self._request_sender)

        # 如果不指定resource_type的值,则认为上传的是媒体文件,使用UploadMedia上传
        return UploadMedia(self._file_request, self._request_sender)
