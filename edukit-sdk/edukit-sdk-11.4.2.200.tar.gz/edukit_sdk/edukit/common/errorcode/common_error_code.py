#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.errorcode.abstract_error_code import \
    AbstractErrorCode


class CommonErrorCode(AbstractErrorCode):
    SUCCESS = {-0x38230000: 'Operation success.'}
    SYSTEM_ERROR = {
        0x0000:
        'System error, please check the log of eduKit SDK for more details.'
    }
    PARTIAL_SUCCESS = {
        0x0001:
        'Partial operations failed, '
        'please check all results to find the cause.'
    }
    CALL_API_INTERFACE_FAILED = {
        0x0002:
        'Call API interface failed, '
        'please check the log of eduKit SDK for more details.'
    }
    UPLOAD_FILES_FAILED = {0x1203: "Call upload interface failed."}
    PARAM_CANNOT_BE_EMPTY = {0x1204: "Parameter can not be empty!"}
    INVALID_COURSE_PARAMS = {0x1205: 'Invalid course params.'}
    INVALID_COURSE_CANCEL_COMMIT_ACTION = {
        0x1206:
        'Invalid course params, '
        'please create course first '
        'or check the updating course params.'
    }
    LESSON_ID_EMPTY = {0x1207: "Lesson ID can not be empty!"}
    NO_SUCCESSFUL_OPERATION = {
        0x1303:
        'There is no successful operation, '
        'please check all results and logs to find the cause.'
    }
    PKG_INPUT_PARAMS_INVALID = {
        0x1305: 'PkgMetaData or pkgEditData can not be null when creating pkg.'
    }
    PKG_ID_INVALID = {0x1306: 'PkgId is invalid.'}
    PKG_EDIT_ID_INVALID = {0x1307: 'Pkg edit_id is invalid.'}

    def __init__(self, error):
        self._error_code = ''
        self._error_desc = None
        for k, v in error.items():
            self._error_code = k
            self._error_desc = v

    @property
    def error_code(self):
        """
        :return:error_code
        """
        return self._error_code

    @property
    def error_desc(self):
        """
        :return:error_desc
        """
        return self._error_desc
