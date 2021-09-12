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
from edukit_sdk.edukit.lesson.resp.lesson_create_response import \
    LessonCreateResponse


class LessonCreateRequest:
    def __init__(self, course_id, course_edit_id, lesson, credential_list):
        self._course_id = course_id
        self._course_edit_id = course_edit_id
        self._lesson = lesson
        self._lesson_handler = LessonHandler(
            EduKitRequestSender(credential_list))

    def create_lesson(self):
        rsp = LessonCreateResponse()
        if Helpers.has_empty_param([self._course_id, self._course_edit_id]):
            logging.error(
                'CourseId or CourseEditId can not be null when create lesson.')
            rsp.result = Helpers.build_error_result(
                CommonErrorCode.PARAM_CANNOT_BE_EMPTY)
            return rsp
        logging.info('Create lesson begin, courseId = %s, courseEditId = %s' %
                     (self._course_id, self._course_edit_id))
        create_lesson_result = self._lesson_handler.create_lesson(
            self._course_id, self._course_edit_id, self._lesson)
        rsp.result = create_lesson_result.result

        if create_lesson_result and create_lesson_result and \
                create_lesson_result.result.result_code != \
                CommonConstant.RESULT_SUCCESS:
            logging.error('Create Lesson failed and code:%s result:%s' %
                          (create_lesson_result.result.result_code,
                           create_lesson_result.result.result_desc))
            return rsp

        lesson_id = create_lesson_result.lesson_id
        lesson_edit_id = create_lesson_result.lesson_edit_id

        rsp.lesson_id = lesson_id
        rsp.lesson_edit_id = lesson_edit_id

        return self._lesson_handler.update_lesson_data_create(
            self._course_id, self._course_edit_id, lesson_id, lesson_edit_id,
            self._lesson, rsp)
