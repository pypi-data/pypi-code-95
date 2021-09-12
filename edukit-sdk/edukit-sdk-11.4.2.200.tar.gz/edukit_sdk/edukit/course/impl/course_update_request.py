# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging

from edukit_sdk.edukit.common.constant.common_constant import CommonConstant
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.course.constant.course_constant import CourseConstant
from edukit_sdk.edukit.course.impl.change_course_status_request import \
    ChangeCourseStatusRequest
from edukit_sdk.edukit.course.impl.course_handler import CourseHandler
from edukit_sdk.edukit.course.impl.create_course_result import \
    CreateCourseResult
from edukit_sdk.edukit.course.model.course_edit import CourseEdit
from edukit_sdk.edukit.course.resp.course_update_response import \
    CourseUpdateResponse


class CourseUpdateRequest:
    def __init__(self, course_edit: CourseEdit, credential_list):
        self._course_edit = course_edit
        self._course_handler = CourseHandler(
            EduKitRequestSender(credential_list))
        self._update_course_edit_id = None

    def save_draft(self):
        course_id = None
        if self.is_course_id_valid(self._course_edit):
            course_id = self._course_edit.course.course_id
        update_course_response = CourseUpdateResponse()

        if not course_id:
            logging.error('CourseId can not be null when update course data.')
            update_course_response.result = Helpers.build_error_result(
                CommonErrorCode.INVALID_COURSE_PARAMS)
            return update_course_response

        logging.info('UpdateCourse save_draft task start and courseId:%s' %
                     course_id)
        update_course_edit_result = self.update_course_edit(self._course_edit)
        if not update_course_edit_result:
            update_course_response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return update_course_response

        logging.info('UpdateCourse save_draft task end and courseId:%s' %
                     course_id)
        update_course_response.result = Helpers.build_error_result(
            CommonErrorCode.SUCCESS)
        return update_course_response

    def commit(self, action):
        change_course_status_request = ChangeCourseStatusRequest(action=action)
        if action == CommonConstant.COURSE_COMMIT_ACTION[
                CourseConstant.CANCEL_COMMIT]:
            return self.cancel_course_commit(change_course_status_request)
        else:
            return self.handle_course(change_course_status_request)

    def cancel_course_commit(
            self, change_course_status_request: ChangeCourseStatusRequest):
        logging.info('COURSE_CANCEL_COMMIT action start.')
        course_update_response = CourseUpdateResponse()
        if not self._course_edit or not self._course_edit.course:
            logging.error(
                'CourseId can not be null when cancelling course commit.')
            course_update_response.result = Helpers.build_error_result(
                CommonErrorCode.INVALID_COURSE_PARAMS)
            return course_update_response

        if not self.is_course_id_valid(self._course_edit):
            logging.error(
                'CourseId can not be null when cancelling course commit.')
            course_update_response.result = Helpers.build_error_result(
                CommonErrorCode.INVALID_COURSE_PARAMS)
            return course_update_response

        course_id = self._course_edit.course.course_id

        course_edit_id = None
        if self._course_edit.course_edit_id:
            course_edit_id = self._course_edit.course_edit_id

        if not course_id or not course_edit_id:
            logging.error(
                'Course EditId is null when cancelling course commit.')
            course_update_response.result = Helpers.build_error_result(
                CommonErrorCode.INVALID_COURSE_CANCEL_COMMIT_ACTION)
            return course_update_response

        course_update_response.course_id = course_id
        course_update_response.edit_id = course_edit_id
        course_update_response.result = Helpers.build_error_result(
            CommonErrorCode.SUCCESS)

        course_update_response = self.course_commit(
            course_update_response, change_course_status_request)

        logging.info('COURSE_CANCEL_COMMIT action end and courseId:%s' %
                     course_id)
        return course_update_response

    def handle_course(self,
                      change_course_status_request: ChangeCourseStatusRequest):
        course_update_response = CourseUpdateResponse()
        if not self.is_course_id_valid(self._course_edit):
            logging.error('CourseId can not be null when update course data.')
            course_update_response.result = Helpers.build_error_result(
                CommonErrorCode.INVALID_COURSE_PARAMS)
            return course_update_response

        course_id = self._course_edit.course.course_id

        logging.info('UpdateCourse commit task start and courseId:%s' %
                     course_id)

        update_course_edit_result = self.update_course_edit(self._course_edit)

        if not update_course_edit_result:
            course_update_response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return course_update_response

        course_update_response.course_id = update_course_edit_result[
            CourseConstant.COURSE_Id]
        course_update_response.edit_id = update_course_edit_result[
            CourseConstant.COURSE_EDIT_ID]
        course_update_response.result = Helpers.build_error_result(
            CommonErrorCode.SUCCESS)

        course_update_response = self.course_commit(
            course_update_response, change_course_status_request)
        logging.info('UpdateCourse commit task end and courseId:%s' %
                     course_id)
        return course_update_response

    def create_new_edit(self):
        return self._course_handler.create_new_course_edit(self._course_edit)

    def update_course_edit(self, course_edit: CourseEdit):
        if self.need_create_new_edit(course_edit):
            new_course_edit = self._course_handler.create_new_course_edit(
                course_edit)
            if new_course_edit.result.result_code != \
                    CommonConstant.RESULT_SUCCESS:
                logging.error(
                    'Get wrong result from create courseNewEdit interface '
                    'and courseId:%s,wrong result:%s'
                    % (course_edit.course.course_id,
                       new_course_edit.result.result_desc))
                return False
            edit_id = new_course_edit.edit_id
        else:
            edit_id = course_edit.course_edit_id

        create_course_result = CreateCourseResult(
            edit_id=edit_id, course_id=course_edit.course.course_id)

        if not self._course_handler.update_course_edit(course_edit,
                                                       create_course_result):
            return False

        return {
            CourseConstant.COURSE_Id: course_edit.course.course_id,
            CourseConstant.COURSE_EDIT_ID: edit_id
        }

    def course_commit(self, course_update_response: CourseUpdateResponse,
                      change_course_status_request: ChangeCourseStatusRequest):
        commit_result = self._course_handler.commit_course(
            course_update_response.course_id, course_update_response.edit_id,
            self._course_edit.course, change_course_status_request)

        if commit_result and commit_result.result_code != \
                CommonConstant.RESULT_SUCCESS:
            course_update_response.result = Helpers.build_error_result(
                CommonErrorCode.PARTIAL_SUCCESS)

        course_update_response.commit_result = commit_result
        return course_update_response

    @staticmethod
    def need_create_new_edit(course_edit: CourseEdit):
        return False if course_edit.course_edit_id else True

    @staticmethod
    def is_course_id_valid(course_edit: CourseEdit):
        return True if course_edit and course_edit.course and \
                       course_edit.course.course_id else False
