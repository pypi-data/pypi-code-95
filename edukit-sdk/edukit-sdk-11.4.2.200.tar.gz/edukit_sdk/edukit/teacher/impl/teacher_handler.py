#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
import json
import logging

from edukit_sdk.edukit.common.constant.api_constant import ApiConstant
from edukit_sdk.edukit.common.constant.common_constant import CommonConstant
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.errorcode.teacher_error_code import \
    TeacherErrorCode
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.file_upload.file_upload import FileUpload
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.common.http.http_common_response import \
    HttpCommonResponse
from edukit_sdk.edukit.common.model.image_file_info import ImageFileInfo
from edukit_sdk.edukit.teacher.impl.teacher_commit_request import \
    TeacherCommitRequest
from edukit_sdk.edukit.teacher.impl.teacher_create_result import \
    TeacherCreateResult
from edukit_sdk.edukit.teacher.impl.teacher_update_localized_data_request \
    import TeacherUpdateLocalizedDataRequest
from edukit_sdk.edukit.teacher.model.teacher import Teacher
from edukit_sdk.edukit.teacher.model.teacher_basic_info import TeacherBasicInfo
from edukit_sdk.edukit.teacher.model.teacher_edit import TeacherEdit
from edukit_sdk.edukit.teacher.model.teacher_localized_data import \
    TeacherLocalizedData
from edukit_sdk.edukit.teacher.resp.teacher_update_response import \
    TeacherUpdateResponse


class TeacherHandler:
    def __init__(self, request_sender: EduKitRequestSender):
        self._request_sender = request_sender

    def create_teacher(self, teacher: Teacher):
        response = TeacherCreateResult()
        if not teacher:
            response.result = Helpers.build_error_result(
                TeacherErrorCode.INVALID_TEACHER_PARAMS_TEACHER)
            return response

        if not teacher.dev_teacher_id:
            response.result = Helpers.build_error_result(
                TeacherErrorCode.INVALID_TEACHER_PARAMS_DEV_TEACHER_ID)
            return response
        logging.info('Begin to create teacher!')

        teacher_basic_info = TeacherBasicInfo()
        teacher_basic_info.dev_teacher_id = teacher.dev_teacher_id

        url = ApiConstant.CREATE_TEACHER_URL
        try:
            http_common_response = HttpCommonResponse(
                self._request_sender.post(
                    url=url, body=teacher_basic_info.to_json_string()))
            response = Helpers.parse_response(
                http_common_response.get_rsp(),
                'edukit_sdk.edukit.teacher.impl.teacher_create_result.'
                'TeacherCreateResult'
            )
        except EduKitException as e:
            logging.error(
                'Call create teacher interface failed. ErrorMessage: %s' %
                str(e))
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return response
        return response

    def update_teacher(self, teacher: Teacher,
                       teacher_create_result: TeacherCreateResult):
        response = TeacherUpdateResponse()
        if teacher.teacher_metadata:
            response.update_metadata_result = self._update_metadata(
                teacher, teacher_create_result)
            if response.update_metadata_result.result_code != \
                    CommonConstant.RESULT_SUCCESS:
                return response

        if teacher.teacher_multi_language_data_list:
            response.update_localized_data_result = \
                self._update_localized_data_list(
                    teacher.teacher_multi_language_data_list,
                    teacher_create_result)
            if response.update_localized_data_result.result_code != \
                    CommonConstant.RESULT_SUCCESS:
                return response

        if teacher.language_list_to_delete:
            response.delete_localized_data_result = \
                self._delete_localized_data(
                    teacher.language_list_to_delete,
                    teacher_create_result.teacher_id,
                    teacher_create_result.edit_id)

        return response

    def commit(self, teacher_id, edit_id):
        logging.info('Begin to commit teacher,teacher_id:%s, edit_id:%s' %
                     (teacher_id, edit_id))
        teacher_commit_request = TeacherCommitRequest()
        teacher_commit_request.teacher_id = teacher_id
        teacher_commit_request.edit_id = edit_id
        url = ApiConstant.COMMIT_TEACHER_URL
        try:
            http_common_response = HttpCommonResponse(
                self._request_sender.post(
                    url=url, body=teacher_commit_request.to_json_string()))
        except EduKitException as e:
            logging.error('Commit teacher failed. ErrorMessage: %s' % str(e))
            return Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
        return Helpers.build_result(http_common_response.get_rsp())

    def update_teacher_basic_info(self, teacher_id, dev_teacher_id):
        logging.info(
            'Begin to update teacher basic info, teacher_id:%s, '
            'dev_teacher_id:%s'
            % (teacher_id, dev_teacher_id))
        headers = dict()
        if teacher_id:
            headers['teacherId'] = teacher_id
        teacher_basic_info = TeacherBasicInfo()
        teacher_basic_info.dev_teacher_id = dev_teacher_id
        url = ApiConstant.CREATE_TEACHER_URL
        try:
            http_common_response = HttpCommonResponse(
                self._request_sender.put(
                    url=url,
                    body=teacher_basic_info.to_json_string(),
                    headers=headers))
        except EduKitException as e:
            logging.error(
                'Update teacher basic info failed. ErrorMessage: %s' % str(e))
            return Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
        return Helpers.build_result(http_common_response.get_rsp())

    def create_teacher_edit(self, teacher_edit: TeacherEdit):
        teacher_id = '' if not teacher_edit \
                           or not teacher_edit.teacher \
                           or not teacher_edit.teacher.teacher_id \
                           else teacher_edit.teacher.teacher_id
        dev_teacher_id = '' if not teacher_edit or not \
            teacher_edit.teacher or not teacher_edit.teacher.dev_teacher_id \
            else teacher_edit.teacher.dev_teacher_id
        logging.info(
            'Begin to create new teacher edit, teacher_id:%s, '
            'dev_teacher_id:%s.'
            % (teacher_id, dev_teacher_id))
        rsp = TeacherUpdateResponse()
        headers = dict()
        headers['teacherId'] = teacher_id
        if dev_teacher_id:
            headers['devTeacherId'] = dev_teacher_id
        url = ApiConstant.CREATE_NEW_TEACHER_EDIT_URL
        try:
            http_common_response = HttpCommonResponse(
                self._request_sender.post(url=url, headers=headers))
        except EduKitException as e:
            logging.error(
                'Create new teacher edit failed, teacher_id:%s. '
                'ErrorMessage: %s'
                % (teacher_id, str(e)))
            rsp.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return rsp
        rsp.teacher_id = teacher_id

        rsp.result = Helpers.build_result(http_common_response.get_rsp())
        if rsp.result.result_code != CommonConstant.RESULT_SUCCESS:
            logging.error(
                'create teacher edit failed! result_code: %s, result_desc: %s'
                % (rsp.result.result_code, rsp.result.result_desc))
        else:
            rsp.teacher_edit_id = http_common_response.get_rsp()['editId']
        return rsp

    def delete(self, teacher_id, reason):
        if not teacher_id:
            return Helpers.build_error_result(
                TeacherErrorCode.INVALID_TEACHER_PARAMS_TEACHER_ID)

        url = ApiConstant.DELETE_TEACHER_URL.format(teacher_id)
        body = {"reason": reason}
        body = bytes(json.dumps(body), encoding='utf-8')
        try:
            http_common_response = HttpCommonResponse(
                self._request_sender.post(url=url, body=body))
        except EduKitException as e:
            logging.error(
                'Delete teacher failed, teacher_id:%s. ErrorMessage: %s' %
                (teacher_id, str(e)))
            return Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
        return Helpers.build_result(http_common_response.get_rsp())

    def _update_metadata(self, teacher: Teacher,
                         teacher_create_result: TeacherCreateResult):
        dev_teacher_id = teacher.dev_teacher_id
        teacher_id = teacher_create_result.teacher_id
        teacher_edit_id = teacher_create_result.edit_id
        if not teacher_id:
            teacher_id = dev_teacher_id
        logging.info(
            'Begin to update teacher metadata, teacherId: %s, teacherEditId:%s'
            % (teacher_id, teacher_edit_id))
        try:
            url = ApiConstant.UPDATE_META_TEACHER_URL.format(
                teacher_id, teacher_edit_id)
            http_common_response = HttpCommonResponse(
                self._request_sender.put(
                    url=url, body=teacher.teacher_metadata.to_json_string()))
        except EduKitException as e:
            logging.error(
                'Call update teacher metadata interface failed. '
                'ErrorMessage: %s'
                % str(e))
            return Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
        return Helpers.build_result(http_common_response.get_rsp())

    def _update_localized_data_list(
            self, teacher_multi_language_data_list,
            teacher_create_result: TeacherCreateResult):
        response = Helpers.build_error_result(CommonErrorCode.SUCCESS)
        teacher_id = teacher_create_result.teacher_id
        teacher_edit_id = teacher_create_result.edit_id
        logging.info(
            'Begin to update teacher localized data, teacherId: %s, '
            'teacherEditId:%s'
            % (teacher_id, teacher_edit_id))
        for teacher_multi_language_data in teacher_multi_language_data_list:
            if teacher_multi_language_data.teacher_portrait:
                upload_result = self._upload_portrait(
                    teacher_multi_language_data.teacher_portrait)
                if not upload_result:
                    response = Helpers.build_error_result(
                        CommonErrorCode.UPLOAD_FILES_FAILED)
                    break
                teacher_multi_language_data.portrait_id = upload_result

            update_localized_data_result = self._update_localized_data(
                teacher_multi_language_data, teacher_id, teacher_edit_id,
                teacher_multi_language_data.language)
            if update_localized_data_result.result_code != \
                    CommonConstant.RESULT_SUCCESS:
                response = update_localized_data_result
                break
        return response

    def _update_localized_data(
            self, teacher_multi_language_data: TeacherLocalizedData,
            teacher_id, teacher_edit_id, language):
        update_localized_data_request = TeacherUpdateLocalizedDataRequest()
        update_localized_data_request.localized_data = \
            teacher_multi_language_data
        try:
            url = ApiConstant.UPDATE_LOCALIZED_TEACHER_URL.format(
                teacher_id, teacher_edit_id, language)
            http_common_response = HttpCommonResponse(
                self._request_sender.put(
                    url=url,
                    body=update_localized_data_request.to_json_string()))
        except EduKitException as e:
            logging.error(
                'Update teacher localized data failed. ErrorMessage: %s' %
                str(e))
            return Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
        return Helpers.build_result(http_common_response.get_rsp())

    def _delete_localized_data(self, language_list, teacher_id,
                               teacher_edit_id):
        response = Helpers.build_error_result(CommonErrorCode.SUCCESS)
        logging.info(
            'Begin to delete teacher localized data, teacherId: %s, '
            'teacherEditId:%s'
            % (teacher_id, teacher_edit_id))
        for language in language_list:
            url = ApiConstant.DELETE_LOCALIZED_TEACHER_URL.format(
                teacher_id, teacher_edit_id, language)
            try:
                http_common_response = HttpCommonResponse(
                    self._request_sender.delete(url=url))
            except EduKitException as e:
                logging.error(
                    'Delete teacher localized data failed. ErrorMessage: %s' %
                    str(e))
                return Helpers.build_error_result(
                    CommonErrorCode.CALL_API_INTERFACE_FAILED)

            if not Helpers.is_success(http_common_response.get_rsp()):
                response = Helpers.build_result(http_common_response.get_rsp())
                break
        return response

    def _upload_portrait(self, portrait: ImageFileInfo):
        try:
            file_upload = FileUpload(path=portrait.path,
                                     resource_type=portrait.resource_type,
                                     request_sender=self._request_sender)
            result = file_upload.upload()
        except EduKitException as e:
            logging.error('Upload teacher portrait failed. ErrorMessage: %s' %
                          str(e))
            return False
        if not Helpers.is_success(result):
            logging.error('Upload teacher portrait failed. errMsg: %s' %
                          result['result']['resultDesc'])
            return False

        return result['materialId']
