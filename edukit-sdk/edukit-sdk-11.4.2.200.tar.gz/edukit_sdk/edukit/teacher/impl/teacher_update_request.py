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
from edukit_sdk.edukit.teacher.impl.teacher_create_result import \
    TeacherCreateResult
from edukit_sdk.edukit.teacher.impl.teacher_handler import TeacherHandler
from edukit_sdk.edukit.teacher.model.teacher import Teacher
from edukit_sdk.edukit.teacher.model.teacher_edit import TeacherEdit
from edukit_sdk.edukit.teacher.resp.teacher_update_response import \
    TeacherUpdateResponse


class TeacherUpdateRequest:
    def __init__(self, teacher_edit: TeacherEdit, credential_list):
        self._teacher_edit = teacher_edit
        self._teacher_handler = TeacherHandler(
            EduKitRequestSender(credential_list))

    def save_draft(self):
        teacher_update_rsp = TeacherUpdateResponse()
        logging.info('Update teacher begin')
        if not self._teacher_edit or not self._teacher_edit.teacher \
                or not self._teacher_edit.teacher.teacher_id:
            logging.error('Teacher_id can not be null when updating teacher.')
            teacher_update_rsp.result = Helpers.build_error_result(
                TeacherErrorCode.INVALID_TEACHER_PARAMS_TEACHER_ID)
            return teacher_update_rsp

        dev_teacher_id = '' if not self._teacher_edit or not \
            self._teacher_edit.teacher or not \
            self._teacher_edit.teacher.dev_teacher_id else \
            self._teacher_edit.teacher.dev_teacher_id

        self.__update_teacher_edit(self._teacher_edit.teacher,
                                   self._teacher_edit.teacher.teacher_id,
                                   dev_teacher_id, teacher_update_rsp)

        return teacher_update_rsp

    def commit(self):
        teacher_update_rsp = self.save_draft()
        if teacher_update_rsp.result.result_code != \
                CommonConstant.RESULT_SUCCESS:
            return teacher_update_rsp

        commit_result = self._teacher_handler.commit(
            self._teacher_edit.teacher.teacher_id,
            teacher_update_rsp.teacher_edit_id)
        teacher_update_rsp.teacher_commit_result = commit_result
        if commit_result.result_code != CommonConstant.RESULT_SUCCESS:
            teacher_update_rsp.result = Helpers.build_error_result(
                CommonErrorCode.PARTIAL_SUCCESS)
        else:
            teacher_update_rsp.result = Helpers.build_error_result(
                CommonErrorCode.SUCCESS)

        return teacher_update_rsp

    def __update_teacher_edit(self, teacher: Teacher, teacher_id,
                              dev_teacher_id, rsp: TeacherUpdateResponse):
        if dev_teacher_id:
            update_basic_info_result = \
                self._teacher_handler.update_teacher_basic_info(
                    teacher_id,
                    dev_teacher_id)
            rsp.update_basic_info_result = update_basic_info_result
            if update_basic_info_result.result_code != \
                    CommonConstant.RESULT_SUCCESS:
                rsp.result = Helpers.build_error_result(
                    CommonErrorCode.NO_SUCCESSFUL_OPERATION)
                return False

        if self.__need_create_new_edit(teacher):
            new_edit = self._teacher_handler.create_teacher_edit(
                self._teacher_edit)
            rsp.create_new_edit_result = new_edit.result
            if new_edit.result.result_code != CommonConstant.RESULT_SUCCESS:
                rsp.result = Helpers.build_error_result(
                    CommonErrorCode.NO_SUCCESSFUL_OPERATION)
                return rsp
            edit_id = new_edit.teacher_edit_id
        else:
            edit_id = self._teacher_edit.teacher_edit_id

        rsp.teacher_edit_id = edit_id
        teacher_create_result = TeacherCreateResult()
        teacher_create_result.teacher_id = teacher_id
        teacher_create_result.edit_id = edit_id
        update_rsp = self._teacher_handler.update_teacher(
            teacher, teacher_create_result)
        rsp.update_metadata_result = update_rsp.update_metadata_result
        rsp.update_localized_data_result = \
            update_rsp.update_localized_data_result
        rsp.delete_localized_data_result = \
            update_rsp.delete_localized_data_result
        if self.__is_update_success(update_rsp):
            rsp.result = Helpers.build_error_result(CommonErrorCode.SUCCESS)
        else:
            rsp.result = Helpers.build_error_result(
                CommonErrorCode.PARTIAL_SUCCESS)
        return rsp

    @staticmethod
    def __is_update_success(update_rsp: TeacherUpdateResponse):
        if update_rsp.update_metadata_result and \
                update_rsp.update_metadata_result.result_code != \
                CommonConstant.RESULT_SUCCESS:
            return False
        if update_rsp.update_localized_data_result and \
                update_rsp.update_localized_data_result.result_code != \
                CommonConstant.RESULT_SUCCESS:
            return False
        if update_rsp.delete_localized_data_result and \
                update_rsp.delete_localized_data_result.result_code != \
                CommonConstant.RESULT_SUCCESS:
            return False

        return True

    def __need_create_new_edit(self, teacher: Teacher):
        return True if not self._teacher_edit.teacher_edit_id and (
                    teacher.teacher_multi_language_data_list
                    or teacher.teacher_metadata
                    or teacher.language_list_to_delete) \
            else False
