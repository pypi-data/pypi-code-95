# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging

from edukit_sdk.edukit.common.constant.api_constant import ApiConstant
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.http_common_response import \
    HttpCommonResponse
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.model.response import Response


class LearningHandler:
    def __init__(self, request_sender):
        self.__request_sender = request_sender

    def report_unitary_course_learning(self, user_id, course_id, user_id_type,
                                       unitary_course_learning_info):
        logging.info(
            "Call reportUnitaryCourseLearning interface start, courseId: %s",
            course_id)
        response = Response()
        try:
            url = ApiConstant.REPORT_UNITARY_COURSE_LEARNING.format(
                user_id, course_id, user_id_type)
            http_common_response = HttpCommonResponse(
                self.__request_sender.put(
                    url=url,
                    body=unitary_course_learning_info.to_json_string()))
            response.result = Helpers.build_result(
                http_common_response.get_rsp())
        except EduKitException as e:
            logging.error(
                u"Call reportUnitaryCourseLearning interface "
                u"failed. ErrorMessage: %s",
                str(e))
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return response
        logging.info(
            "Call reportUnitaryCourseLearning interface end, courseId: %s",
            course_id)
        return response

    def report_series_course_learning(self, user_id, course_id, user_id_type,
                                      lesson_id, series_course_learning_info):
        logging.info(
            "Call reportSeriesCourseLearning interface start, "
            "courseId: %s, lessonId: %s"
            % (course_id, lesson_id))
        response = Response()
        try:
            url = ApiConstant.REPORT_SERIES_COURSE_LEARNING.format(
                user_id, course_id, lesson_id, user_id_type)
            http_common_response = HttpCommonResponse(
                self.__request_sender.put(
                    url=url,
                    body=series_course_learning_info.to_json_string()))
            response.result = Helpers.build_result(
                http_common_response.get_rsp())
        except EduKitException as e:
            logging.error(
                u"Call reportUnitaryCourseLearning interface failed. "
                u"ErrorMessage: %s",
                str(e))
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return response
        logging.info(
            "Call reportUnitaryCourseLearning interface end, courseId: %s",
            course_id)
        return response
