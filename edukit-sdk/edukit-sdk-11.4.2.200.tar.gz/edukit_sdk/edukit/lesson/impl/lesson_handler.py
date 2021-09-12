# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging

from edukit_sdk.edukit.common.constant.api_constant import ApiConstant
from edukit_sdk.edukit.lesson.constant.lesson_constant import LessonConstant
from edukit_sdk.edukit.common.constant.common_constant import CommonConstant
from edukit_sdk.edukit.common.http.http_common_response import \
    HttpCommonResponse
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.lesson.model.lesson import Lesson
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.common.model.response import Response
from edukit_sdk.edukit.common.util.update_data_util import UpdateDataUtil
from edukit_sdk.edukit.course.impl.update_localized_data_request import \
    UpdateLocalizedDataRequest
from edukit_sdk.edukit.lesson.impl.create_lesson_edit_request import \
    CreateLessonEditRequest
from edukit_sdk.edukit.lesson.impl.create_lesson_request import \
    CreateLessonRequest
from edukit_sdk.edukit.lesson.impl.create_lesson_result import \
    CreateLessonResult
from edukit_sdk.edukit.lesson.impl.update_lesson_result import \
    UpdateLessonResult
from edukit_sdk.edukit.lesson.impl.update_meta_data_request import \
    UpdateMetaDataRequest
from edukit_sdk.edukit.lesson.model.lesson_edit import LessonEdit
from edukit_sdk.edukit.lesson.resp.lesson_create_response import \
    LessonCreateResponse
from edukit_sdk.edukit.lesson.resp.lesson_update_response import \
    LessonUpdateResponse


class LessonHandler:
    def __init__(self, request_sender: EduKitRequestSender):
        """
        :param request_sender:
        """
        self._request_sender = request_sender

    def create_lesson(self, course_id, course_edit_id, lesson: Lesson):
        response = CreateLessonResult()
        try:
            url = ApiConstant.LESSON_CREATE_URL.format(course_id,
                                                       course_edit_id)
            create_lesson_request = CreateLessonRequest()
            if lesson.meta_data and lesson.meta_data.display_order:
                create_lesson_request.display_order = \
                    lesson.meta_data.display_order
            if lesson.catalogue_id:
                create_lesson_request.catalogue_id = lesson.catalogue_id
            http_common_response = HttpCommonResponse(
                self._request_sender.post(
                    url=url, body=create_lesson_request.to_bytes()))
            response = Helpers.parse_response(
                http_common_response.get_rsp(),
                LessonConstant.CreateLessonResult)
        except EduKitException as e:
            logging.info(
                'Call create lesson interface failed. ErrorMessage: %s' %
                e.message)
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return response
        return response

    def update_lesson_data(self, course_id, course_edit_id, lesson_id,
                           lesson_edit_id, lesson: Lesson,
                           rsp: LessonUpdateResponse):
        # 更新章节元数据
        update_lesson_meta_data_result = self._update_lesson_meta_data(
            course_id, course_edit_id, lesson_id, lesson_edit_id, lesson)
        rsp.update_lesson_meta_data_result = update_lesson_meta_data_result
        if update_lesson_meta_data_result and \
                update_lesson_meta_data_result.result:
            if update_lesson_meta_data_result.result.result_code != \
                    CommonConstant.RESULT_SUCCESS:
                result_code = update_lesson_meta_data_result.result.result_code
                result_desc = update_lesson_meta_data_result.result.result_desc
                logging.error(
                    'Update lesson metadata failed and result_code: %s,'
                    'error_message: %s  ' % (result_code, result_desc))
                rsp.result = Helpers.build_error_result(
                    CommonErrorCode.PARTIAL_SUCCESS)
                return rsp
            else:
                logging.info('Update lesson metadata end')

        # 更新章节本地化多语言数据
        update_lesson_localized_data_result = \
            self._update_multi_language_data_list(
                course_id, course_edit_id, lesson_id, lesson_edit_id, lesson)
        rsp.update_localized_data_result = update_lesson_localized_data_result
        if update_lesson_localized_data_result and \
                update_lesson_localized_data_result.result:
            if update_lesson_localized_data_result.result.result_code != \
                    CommonConstant.RESULT_SUCCESS:
                logging.error(
                    'Update lesson localized data failed and result_code: %s,'
                    'error_message: %s ' %
                    (update_lesson_localized_data_result.result.result_code,
                     update_lesson_localized_data_result.result.result_desc))
                rsp.result = Helpers.build_error_result(
                    CommonErrorCode.PARTIAL_SUCCESS)
                return rsp
            else:
                logging.info('Update localized data end')

        if lesson.language_list_to_delete:
            delete_localized_data_result = self._delete_localized_data(
                course_id, course_edit_id, lesson_id, lesson_edit_id, lesson)
            rsp.delete_localized_data_result = delete_localized_data_result
            if delete_localized_data_result and \
                    delete_localized_data_result.result and \
                    delete_localized_data_result.result.result_code != \
                    CommonConstant.RESULT_SUCCESS:
                rsp.result = Helpers.build_error_result(
                    CommonErrorCode.PARTIAL_SUCCESS)
                return rsp
        rsp.result = Helpers.build_error_result(CommonErrorCode.SUCCESS)
        return rsp

    def update_lesson_data_create(self, course_id, course_edit_id, lesson_id,
                                  lesson_edit_id, lesson: Lesson,
                                  rsp: LessonCreateResponse):
        update_lesson_meta_data_result = self._update_lesson_meta_data(
            course_id, course_edit_id, lesson_id, lesson_edit_id, lesson)
        rsp.update_lesson_meta_data_result = update_lesson_meta_data_result
        if update_lesson_meta_data_result and \
                update_lesson_meta_data_result.result:
            if update_lesson_meta_data_result.result.result_code != \
                    CommonConstant.RESULT_SUCCESS:
                logging.error(
                    'Update lesson metadata failed and result_code: %s,'
                    'error_message: %s  '
                    % (update_lesson_meta_data_result.result.result_code,
                       update_lesson_meta_data_result.result.result_desc))
                rsp.result = Helpers.build_error_result(
                    CommonErrorCode.PARTIAL_SUCCESS)
                return rsp
            else:
                logging.info('Update lesson metadata end')

        update_create_localized_data_result = \
            self._update_multi_language_data_list(
                course_id, course_edit_id, lesson_id, lesson_edit_id, lesson)

        rsp.update_localized_data_result = update_create_localized_data_result
        if update_create_localized_data_result and \
                update_create_localized_data_result.result:
            if update_create_localized_data_result.result.result_code != \
                    CommonConstant.RESULT_SUCCESS:
                logging.error(
                    'Update lesson localized data failed and result_'
                    'code: %s,error_message: %s '
                    % (update_create_localized_data_result.result.result_code,
                       update_create_localized_data_result.result.result_desc))
                rsp.result = Helpers.build_error_result(
                    CommonErrorCode.PARTIAL_SUCCESS)
                return rsp
            else:
                logging.info('Update lesson localized data end')

        rsp.result = Helpers.build_error_result(CommonErrorCode.SUCCESS)
        return rsp

    def _update_lesson_meta_data(self, course_id, course_edit_id, lesson_id,
                                 lesson_edit_id, lesson: Lesson):
        response = Response()
        if not lesson.meta_data:
            logging.info(
                'Lesson metadata is empty, courseId = %s, courseEditId = %s, '
                'lessonId = %s, lessonEditId = %s.'
                % (course_id, course_edit_id, lesson_id, lesson_edit_id))

            return response
        logging.info(
            'Update lesson metadata begin, courseId = %s, courseEditId = %s, '
            'lessonId = %s, lessonEditId = %s, '
            'lessonName = %s' % (course_id, course_edit_id, lesson_id,
                                 lesson_edit_id, lesson.meta_data.name))

        update_meta_data_request = UpdateMetaDataRequest()
        update_meta_data_request.meta_data = lesson.meta_data

        try:
            url = ApiConstant.LESSON_METADATA_URL.format(
                course_id, course_edit_id, lesson_id, lesson_edit_id)
            http_common_response = HttpCommonResponse(
                self._request_sender.put(
                    url=url, body=update_meta_data_request.to_bytes()))
            response = Helpers.parse_response(http_common_response.get_rsp(),
                                              LessonConstant.RESPONSE)
        except EduKitException as e:
            logging.info(
                'Call update lesson metadata interface failed. '
                'ErrorMessage: %s' % e.message)
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return response
        return response

    def _update_multi_language_data_list(self, course_id, course_edit_id,
                                         lesson_id, lesson_edit_id,
                                         lesson: Lesson):
        response = Response()
        if not lesson.multi_lang_localized_data_list:
            logging.info(
                'Lesson multi_lang_localized_data_list is empty, '
                'courseId = %s, courseEditId = %s, lessonId = %s, '
                'lessonEditId = %s.' %
                (course_id, course_edit_id, lesson_id, lesson_edit_id))

            return response
        logging.info(
            'Update lesson localized data begin, courseId = %s, '
            'courseEditId = %s, lessonId = %s, lessonEditId = %s, '
            % (course_id, course_edit_id, lesson_id, lesson_edit_id))
        response.result = Helpers.build_error_result(CommonErrorCode.SUCCESS)
        for item in lesson.multi_lang_localized_data_list:
            update_localized_data_request = UpdateLocalizedDataRequest()
            update_localized_data_request.localized_data = \
                item.lesson_localized_data
            if item.media_localized_data:
                update_localized_media_result_list = list()
                single_result = UpdateDataUtil.update_multi_language_data(
                    item.media_localized_data, self._request_sender)
                if not single_result:
                    response.result = Helpers.build_error_result(
                        CommonErrorCode.CALL_API_INTERFACE_FAILED)
                    return response
                update_localized_media_result_list.append(single_result)
                update_localized_data_request.localized_media = \
                    update_localized_media_result_list

            update_localized_data_rsp = self._update_localized_data(
                course_id, course_edit_id, lesson_id, lesson_edit_id,
                update_localized_data_request, item.language)
            if update_localized_data_rsp and update_localized_data_rsp.result \
                    and update_localized_data_rsp.result.result_code != \
                    CommonConstant.RESULT_SUCCESS:
                response = update_localized_data_rsp
                break
        return response

    def _update_localized_data(
            self, course_id, course_edit_id, lesson_id, lesson_edit_id,
            update_localized_data_request: UpdateLocalizedDataRequest, lang):
        response = Response()
        try:
            url = ApiConstant.LESSON_LOCALIZED_DATA_URL.format(
                course_id, course_edit_id, lesson_id, lesson_edit_id, lang)
            http_common_response = HttpCommonResponse(
                self._request_sender.put(
                    url=url, body=update_localized_data_request.to_bytes()))
            response = Helpers.parse_response(http_common_response.get_rsp(),
                                              LessonConstant.RESPONSE)
        except EduKitException as e:
            logging.info(
                'Call update lesson localized data interface failed. '
                'ErrorMessage: %s'
                % e.message)
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return response
        return response

    def _delete_localized_data(self, course_id, course_edit_id, lesson_id,
                               lesson_edit_id, lesson: Lesson):
        response = Response()
        for language in lesson.language_list_to_delete:
            logging.info(
                'Delete lesson language begin, courseId = %s, '
                'courseEditId = %s, lessonId = %s, lessonEditId = %s, '
                'language = %s' % (course_id, course_edit_id, lesson_id,
                                   lesson_edit_id, language))
            try:
                url = ApiConstant.LESSON_LOCALIZED_DATA_URL.format(
                    course_id, course_edit_id, lesson_id, lesson_edit_id,
                    language)
                http_common_response = HttpCommonResponse(
                    self._request_sender.delete(url=url))
                result = Helpers.parse_response(http_common_response.get_rsp(),
                                                LessonConstant.RESPONSE)
                if result and result.result and result.result.result_code != \
                        CommonConstant.RESULT_SUCCESS:
                    logging.error(
                        'Delete lesson language failed and courseId = %s, '
                        'courseEditId = %s, '
                        'lessonId = %s, lessonEditId = %s, language = %s, '
                        'result_code: %s,error_message: %s'
                        % (course_id, course_edit_id, lesson_id,
                           lesson_edit_id, language, result.result.result_code,
                           result.result.result_desc))
                    response.result = result.result
                    return response
            except EduKitException as e:
                logging.error(
                    'Delete lesson language failed and courseId = %s, '
                    'courseEditId = %s, '
                    'lessonId = %s, lessonEditId = %s, language = %s, '
                    'errorCode:%s, errormessage:%s'
                    % (course_id, course_edit_id, lesson_id, lesson_edit_id,
                       language, e.message, e.code))
                response.result = Helpers.build_error_result(
                    CommonErrorCode.CALL_API_INTERFACE_FAILED)
                return response
            logging.info(
                'Delete lesson language end, courseId = %s, courseEditId = %s,'
                ' lessonId = %s, lessonEditId = %s, language = %s' %
                (course_id, course_edit_id, lesson_id,
                 lesson_edit_id, language))

        response.result = Helpers.build_error_result(CommonErrorCode.SUCCESS)
        return response

    def create_lesson_new_edit(self, lesson_edit: LessonEdit,
                               force_create_new_edit):
        response = UpdateLessonResult()
        if not lesson_edit.lesson.lesson_id:
            response.result = Helpers.build_error_result(
                CommonErrorCode.LESSON_ID_EMPTY)
            return response
        logging.info('Create lesson new edit begin')
        create_lesson_edit_request = CreateLessonEditRequest()
        create_lesson_edit_request.force_create_new_edit = \
            force_create_new_edit

        try:
            url = ApiConstant.LESSON_URL.format(lesson_edit.course_id,
                                                lesson_edit.course_edit_id,
                                                lesson_edit.lesson.lesson_id)
            http_common_response = HttpCommonResponse(
                self._request_sender.put(
                    url=url, body=create_lesson_edit_request.to_bytes()))
            response = Helpers.parse_response(
                http_common_response.get_rsp(),
                LessonConstant.UPDATE_LESSON_RESULT)
        except EduKitException as e:
            logging.info(
                'Call create lesson new edit interface failed. code:%s '
                'ErrorMessage: %s'
                % (e.code, e.message))
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return response
        return response

    def delete_lesson(self, course_id, course_edit_id, lesson_id):
        logging.info(
            'Delete lesson begin, courseId = %s, courseEditId = %s, '
            'lessonId = %s'
            % (course_id, course_edit_id, lesson_id))
        response = Response()
        try:
            url = ApiConstant.LESSON_URL.format(course_id, course_edit_id,
                                                lesson_id)
            http_common_response = HttpCommonResponse(
                self._request_sender.delete(url=url))
            response = Helpers.parse_response(http_common_response.get_rsp(),
                                              LessonConstant.RESPONSE)
            if response and response.result and response.result.result_code \
                    != CommonConstant.RESULT_SUCCESS:
                logging.error(
                    'Delete lesson failed and result_code: %s,error_message: '
                    '%s' % (response.result.result_code,
                            response.result.result_desc))
                return response
        except EduKitException as e:
            logging.info(
                'Call delete lesson interface failed. ErrorMessage: %s' %
                e.message)
            response.result(
                Helpers.build_error_result(
                    CommonErrorCode.CALL_API_INTERFACE_FAILED))
            return response
        logging.info(
            'Delete lesson end, courseId = %s, courseEditId = %s, '
            'lessonId = %s' % (course_id, course_edit_id, lesson_id))
        return response

    def reset_lesson(self, course_id, course_edit_id, lesson_id):
        logging.info(
            'Reset lesson begin, courseId = %s, courseEditId = %s, '
            'lessonId = %s'
            % (course_id, course_edit_id, lesson_id))
        response = Response()
        try:
            url = ApiConstant.LESSON_RESET_URL.format(course_id,
                                                      course_edit_id,
                                                      lesson_id)
            http_common_response = HttpCommonResponse(
                self._request_sender.delete(url=url))
            response = Helpers.parse_response(http_common_response.get_rsp(),
                                              LessonConstant.RESPONSE)
            if response and response.result and response.result.result_code \
                    != CommonConstant.RESULT_SUCCESS:
                logging.error(
                    'Reset lesson interface failed and result_code: %s,'
                    'error_message: %s'
                    %
                    (response.result.result_code, response.result.result_desc))
                return response
        except EduKitException as e:
            logging.error(
                'Call reset lesson interface failed. ErrorMessage: %s' %
                e.message)
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return response
        logging.info(
            'Reset lesson end, courseId = %s, courseEditId = %s, lessonId = %s'
            % (
                course_id,
                course_edit_id,
                lesson_id,
            ))
        return response
