#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging

from edukit_sdk.edukit.common.constant.common_constant import CommonConstant
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.errorcode.teacher_error_code import \
    TeacherErrorCode
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.teacher.impl.teacher_handler import TeacherHandler
from edukit_sdk.edukit.teacher.model.teacher import Teacher
from edukit_sdk.edukit.teacher.resp.teacher_create_response import \
    TeacherCreateResponse


class TeacherCreateRequest:
    def __init__(self, teacher: Teacher, credential_list):
        self._teacher = teacher
        self._teacher_handler = TeacherHandler(
            EduKitRequestSender(credential_list))

    def save_draft(self):
        teacher_create_rsp = TeacherCreateResponse()
        logging.info('Create teacher begin')
        create_teacher_result = self._teacher_handler.create_teacher(
            self._teacher)
        if create_teacher_result.result.result_code != \
                CommonConstant.RESULT_SUCCESS:
            logging.error('Create teacher failed and result:%s' %
                          create_teacher_result.result.result_desc)
            teacher_create_rsp.teacher_create_result = \
                create_teacher_result.result
            teacher_create_rsp.result = Helpers.build_error_result(
                CommonErrorCode.NO_SUCCESSFUL_OPERATION)
            return teacher_create_rsp

        teacher_create_rsp.teacher_id = create_teacher_result.teacher_id
        teacher_create_rsp.teacher_edit_id = create_teacher_result.edit_id
        if not self._teacher.teacher_multi_language_data_list and not \
                self._teacher.teacher_metadata:
            logging.info(
                'An empty teacher is created and teacherId:%s, editId:%s.' %
                create_teacher_result.teacher_id,
                create_teacher_result.edit_id)
            teacher_create_rsp.result = Helpers.build_error_result(
                CommonErrorCode.SUCCESS)
            return teacher_create_rsp

        update_teacher_result = self._teacher_handler.update_teacher(
            self._teacher, create_teacher_result)
        teacher_create_rsp.teacher_create_result = Helpers.build_error_result(
            CommonErrorCode.SUCCESS)
        teacher_create_rsp.update_metadata_result = \
            update_teacher_result.update_metadata_result
        teacher_create_rsp.update_localized_data_result = \
            update_teacher_result.update_localized_data_result
        teacher_create_rsp.result = Helpers.build_error_result(
            CommonErrorCode.SUCCESS)
        if (update_teacher_result.update_metadata_result.result_code !=
                CommonConstant.RESULT_SUCCESS or
                update_teacher_result.update_localized_data_result.result_code
                != CommonConstant.RESULT_SUCCESS):
            teacher_create_rsp.result = Helpers.build_error_result(
                CommonErrorCode.PARTIAL_SUCCESS)

        return teacher_create_rsp

    def commit(self):
        teacher_create_rsp = TeacherCreateResponse()
        if not self._teacher.teacher_metadata:
            logging.error(
                'Teacher metaData can not be null when creating teacher '
                'to commit.'
            )
            teacher_create_rsp.result = Helpers.build_error_result(
                TeacherErrorCode.INVALID_TEACHER_PARAMS_MATA_DATA)
            return teacher_create_rsp

        if not self._teacher.teacher_multi_language_data_list:
            logging.error(
                'Teacher localizedData can not be null when creating teacher '
                'to commit.'
            )
            teacher_create_rsp.result = Helpers.build_error_result(
                TeacherErrorCode.INVALID_TEACHER_PARAMS_LOCALIZED_DATA)
            return teacher_create_rsp

        create_teacher_result = self._teacher_handler.create_teacher(
            self._teacher)
        teacher_create_rsp.teacher_create_result = create_teacher_result.result
        if create_teacher_result.result.result_code != \
                CommonConstant.RESULT_SUCCESS:
            logging.error('Create teacher failed and result:%s' %
                          create_teacher_result.result)
            teacher_create_rsp.result = Helpers.build_error_result(
                CommonErrorCode.NO_SUCCESSFUL_OPERATION)
            return teacher_create_rsp

        update_teacher_result = self._teacher_handler.update_teacher(
            self._teacher, create_teacher_result)
        teacher_create_rsp.teacher_id = create_teacher_result.teacher_id
        teacher_create_rsp.teacher_edit_id = create_teacher_result.edit_id
        teacher_create_rsp.update_metadata_result = \
            update_teacher_result.update_metadata_result
        teacher_create_rsp.update_localized_data_result = \
            update_teacher_result.update_localized_data_result

        commit_result = self._teacher_handler.commit(
            create_teacher_result.teacher_id, create_teacher_result.edit_id)
        teacher_create_rsp.teacher_commit_result = commit_result
        teacher_create_rsp.result = Helpers.build_error_result(
            CommonErrorCode.SUCCESS)
        if commit_result.result_code != CommonConstant.RESULT_SUCCESS:
            teacher_create_rsp.result = Helpers.build_error_result(
                CommonErrorCode.PARTIAL_SUCCESS)

        return teacher_create_rsp
