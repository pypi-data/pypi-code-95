# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.common.model.response import Response
from edukit_sdk.edukit.lesson.impl.lesson_handler import LessonHandler


class LessonDeleteRequest:
    def __init__(self, course_id, course_edit_id, lesson_id, credential_list):
        self._course_id = course_id
        self._course_edit_id = course_edit_id
        self._lesson_id = lesson_id
        self._lesson_handler = LessonHandler(
            EduKitRequestSender(credential_list))

    def delete_lesson(self):

        if self.check_parm_has_empty():
            rsp = Response()
            rsp.result = Helpers.build_error_result(
                CommonErrorCode.PARAM_CANNOT_BE_EMPTY)
            return rsp
        return self._lesson_handler.delete_lesson(self._course_id,
                                                  self._course_edit_id,
                                                  self._lesson_id)

    def reset_lesson(self):
        if self.check_parm_has_empty():
            rsp = Response()
            rsp.result = Helpers.build_error_result(
                CommonErrorCode.PARAM_CANNOT_BE_EMPTY)
            return rsp
        return self._lesson_handler.reset_lesson(self._course_id,
                                                 self._course_edit_id,
                                                 self._lesson_id)

    def check_parm_has_empty(self):
        if Helpers.has_empty_param(
                [self._course_id, self._course_edit_id, self._lesson_id]):
            logging.error(
                'CourseId or CourseEditId or LessonId can not be null '
                'when create lesson.'
            )
            return True
        else:
            return False
