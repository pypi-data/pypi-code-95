#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.errorcode.abstract_error_code import \
    AbstractErrorCode


class TeacherErrorCode(AbstractErrorCode):
    INVALID_TEACHER_PARAMS_TEACHER = {0x1501: 'Teacher can not be null.'}
    INVALID_TEACHER_PARAMS_TEACHER_ID = {0x1502: 'Teacher ID can be null.'}
    INVALID_TEACHER_PARAMS_DEV_TEACHER_ID = {
        0x1503: 'DevTeacherId can not be null.'
    }
    INVALID_TEACHER_PARAMS_MATA_DATA = {0x1505: 'MataData can not be null.'}
    INVALID_TEACHER_PARAMS_LOCALIZED_DATA = {
        0x1506: 'LocalizedData can not be null, please check.'
    }

    def _init_(self, error):
        self._errorCode = ''
        self._errorDesc = None
        for k, v in error.items():
            self._errorCode = k
            self._errorDesc = v

    def get_error_code(self):
        """
        获取错误编码，后4位
        :return:errorCode
        """
        return self._errorCode

    def get_error_desc(self):
        """
        获取错误描述
        :return:errorDesc
        """
        return self._errorDesc
