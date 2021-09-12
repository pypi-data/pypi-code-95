# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging

from edukit_sdk.edukit.common.constant.common_constant import CommonConstant
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.course.impl.change_course_status_request import \
    ChangeCourseStatusRequest
from edukit_sdk.edukit.course.impl.course_handler import CourseHandler
from edukit_sdk.edukit.course.impl.create_course_result import \
    CreateCourseResult
from edukit_sdk.edukit.course.model.course import Course
from edukit_sdk.edukit.course.resp.course_create_response import \
    CourseCreateResponse


class CourseCreateRequest:
    def __init__(self, course: Course, credential_list):
        self._course = course
        self._course_handler = CourseHandler(
            EduKitRequestSender(credential_list))

    def save_draft(self):
        logging.info('CreatCourse saveDraft task start.')
        create_course_result = self._course_handler.create_course()
        course_create_response = CourseCreateResponse()
        if create_course_result and create_course_result.result and \
                create_course_result.result.result_code != \
                CommonConstant.RESULT_SUCCESS:
            logging.error('CreateCourse failed and result: %s',
                          create_course_result.result)
            course_create_response.result = create_course_result.result
            return course_create_response

        if not self._course:
            logging.info(
                'An empty course is created and course_id:%s, edit_id:%s',
                create_course_result.course_id, create_course_result.edit_id)
            course_create_response.course_id(create_course_result.course_id)
            course_create_response.edit_id(create_course_result.edit_id)
            course_create_response.result = Helpers.build_error_result(
                CommonErrorCode.SUCCESS)
            return course_create_response

        update_course_result = self._course_handler.update_course(
            self._course, create_course_result)
        if update_course_result:
            course_create_response.edit_id = create_course_result.edit_id
            course_create_response.course_id = create_course_result.course_id
            course_create_response.update_localized_data_result = \
                Helpers.build_error_result(
                    CommonErrorCode.SUCCESS)
            course_create_response.update_meta_data_result = \
                Helpers.build_error_result(
                    CommonErrorCode.SUCCESS)
            course_create_response.result = Helpers.build_error_result(
                CommonErrorCode.SUCCESS)
            course_create_response.update_product_price_result = \
                Helpers.build_error_result(
                    CommonErrorCode.SUCCESS)
        else:
            course_create_response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
        logging.info('CreatCourse saveDraft task end.')
        return course_create_response

    def commit(self, action):
        course_create_response = CourseCreateResponse()
        create_course_result = self._course_handler.create_course()
        if create_course_result and create_course_result.result and \
                create_course_result.result.result_code != \
                CommonConstant.RESULT_SUCCESS:
            logging.error('CreateCourse failed and result: %s',
                          create_course_result.result.result_desc)
            course_create_response.result = create_course_result.result
            return course_create_response

        logging.info('CreatCourse commit task start.')
        change_course_status_request = ChangeCourseStatusRequest()
        change_course_status_request.action = action
        if not self._check_create_course_params(create_course_result,
                                                course_create_response):
            return course_create_response

        update_course_result = self._course_handler.update_course(
            self._course, create_course_result)
        if not update_course_result:
            course_create_response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return course_create_response

        course_create_response.course_id = create_course_result.course_id
        course_create_response.edit_id = create_course_result.edit_id
        course_create_response.update_meta_data_result = \
            Helpers.build_error_result(
                CommonErrorCode.SUCCESS)
        course_create_response.update_localized_data_result = \
            Helpers.build_error_result(
                CommonErrorCode.SUCCESS)
        course_create_response.update_product_price_result = \
            Helpers.build_error_result(
                CommonErrorCode.SUCCESS)
        course_create_response.result = Helpers.build_error_result(
            CommonErrorCode.SUCCESS)

        return self._course_commit(course_create_response,
                                   change_course_status_request)

    def _check_create_course_params(
            self, create_course_result: CreateCourseResult,
            course_create_response: CourseCreateResponse):
        if not self._course:
            logging.error(
                'Course can not be null when committing course and '
                'course_id:%s, edit_id:%s' %
                (create_course_result.course_id, create_course_result.edit_id))
            course_create_response.result = Helpers.build_error_result(
                CommonErrorCode.INVALID_COURSE_PARAMS)
            return False

        if not self._course.course_meta_data:
            logging.error(
                'Course metaData can not be null when committing course '
                'and course_id:%s, edit_id:%s' %
                (create_course_result.course_id, create_course_result.edit_id))
            course_create_response.result = Helpers.build_error_result(
                CommonErrorCode.INVALID_COURSE_PARAMS)
            return False

        if not self._course.course_multi_language_data_list:
            logging.error(
                'Course localizedData can not be null when committing course '
                'and course_id:%s, edit_id:%s' %
                (create_course_result.course_id, create_course_result.edit_id))
            course_create_response.result = Helpers.build_error_result(
                CommonErrorCode.INVALID_COURSE_PARAMS)
            return False

        return True

    def _course_commit(
            self, course_create_response: CourseCreateResponse,
            change_course_status_request: ChangeCourseStatusRequest):
        if course_create_response and course_create_response.result and \
                course_create_response.result.result_code != \
                CommonConstant.RESULT_SUCCESS:
            return course_create_response

        commit_result = self._course_handler.commit_course(
            course_create_response.course_id, course_create_response.edit_id,
            self._course, change_course_status_request)
        if commit_result and commit_result.result_code != \
                CommonConstant.RESULT_SUCCESS:
            course_create_response.result = Helpers.build_error_result(
                CommonErrorCode.PARTIAL_SUCCESS)

        course_create_response.commit_result = commit_result

        logging.info('CreatCourse commit task end.')
        return course_create_response
