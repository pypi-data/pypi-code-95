#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class ErrorConstant:
    # 文件相关
    FILE_UPLOAD_ERROR = 'The file upload failed!'
    FILE_NOT_EXISTS = 'File or directory {} does not exists!'
    PATH_NOT_NULL = 'The file path can not be null!'
    PATH_NOT_ABSOLUTE = 'The file path is not absolute!'
    PATH_IS_DIRECTORY = '{} is a directory!'
    FILE_TYPE_OR_PUBLIC_FILE_NOT_NULL = \
        'The element fileType and publicFile should be null ' \
        'when resourceType has value!'
    RESOURCE_TYPE_IS_INVALID = 'The resourceType is invalid'
    FILE_TYPE_NO_VALUE = 'The element fileType should have value ' \
                         'when resourceType is null!'
    FILE_TYPE_ERROR = "The file type to be uploaded is not supported."
    PICTURE_FILE_TYPE_ERROR = "The file type to be uploaded is not" \
                              " supported, that must be one of .png, .jpg."
    MEDIA_FILE_TYPE_ERROR = "The file type to be uploaded is not supported," \
                            " that must be one of .mp3, .mp4, .wav, .mov."

    # 文件
    CREDENTIAL_IS_EMPTY = 'The credential can not be empty!'
    PARAM_CANNOT_BE_EMPTY = 'The input parameters can not be empty!'
