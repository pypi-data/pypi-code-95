# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging

from edukit_sdk.edukit.common.constant.common_constant import CommonConstant
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.lesson.impl.lesson_handler import LessonHandler
from edukit_sdk.edukit.lesson.model.lesson_edit import LessonEdit
from edukit_sdk.edukit.lesson.resp.lesson_update_response import \
    LessonUpdateResponse


class LessonUpdateRequest:
    def __init__(self,
                 lesson_edit: LessonEdit,
                 credential_list):
        self._lesson_edit = lesson_edit
        self._force_create_new_edit = True
        self._lesson_handler = LessonHandler(
            EduKitRequestSender(credential_list))
        self._lesson_edit_id = None

    def update_lesson(self):
        rsp = LessonUpdateResponse()
        if Helpers.has_empty_param([
                self._lesson_edit.course_id, self._lesson_edit.course_edit_id,
                self._lesson_edit.lesson
        ]):
            logging.error(
                'CourseId or CourseEditId or Lesson can not be null '
                'when create lesson.'
            )
            rsp.result = Helpers.build_error_result(
                CommonErrorCode.PARAM_CANNOT_BE_EMPTY)
            return rsp
        if not self._lesson_edit_id:
            self._lesson_edit_id = self._lesson_edit.lesson_edit_id

        if not self._lesson_edit_id:
            result = self._lesson_handler.create_lesson_new_edit(
                self._lesson_edit, self._force_create_new_edit)
            if result and result.result and result.result.result_code != \
                    CommonConstant.RESULT_SUCCESS:
                logging.error(
                    'Create lesson new edit version failed and code:%s '
                    'message:%s'
                    % (result.result.result_code, result.result.result_desc))
                rsp.result = result.result
                return rsp
            self._lesson_edit_id = result.lesson_edit_id

        rsp.lesson_id = self._lesson_edit.lesson.lesson_id
        rsp.lesson_edit_id = self._lesson_edit_id

        return self._lesson_handler.update_lesson_data(
            self._lesson_edit.course_id, self._lesson_edit.course_edit_id,
            self._lesson_edit.lesson.lesson_id, self._lesson_edit_id,
            self._lesson_edit.lesson, rsp)
