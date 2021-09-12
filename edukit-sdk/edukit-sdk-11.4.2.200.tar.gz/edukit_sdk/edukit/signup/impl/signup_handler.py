# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging

from edukit_sdk.edukit.common.constant.api_constant import ApiConstant
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.http_common_response import \
    HttpCommonResponse
from edukit_sdk.edukit.common.model.response import Response


class SignupHandler:
    def __init__(self, request_sender):
        """
        :param request_sender:相关类
        """
        self.__request_sender = request_sender

    def report_signup(self, user_id, course_id, user_id_type, signup_info):
        """
        :param user_id:用户华为帐号ID
        :param course_id:课程ID
        :param user_id_type:user_id字段对应的帐号类型
        :param signup_info:相关类
        :return: response
        """
        logging.info(u"Call report_signup interface start, course_id: %s",
                     course_id)
        response = Response()
        try:
            url = ApiConstant.REPORT_SIGNUP.format(user_id, course_id,
                                                   user_id_type)
            http_common_response = HttpCommonResponse(
                self.__request_sender.put(url=url,
                                          body=signup_info.to_json_string()))
            response.result = Helpers.build_result(
                http_common_response.get_rsp())
        except EduKitException as e:
            logging.error(
                u'Call reportSignup interface failed. ErrorMessage: %s',
                str(e))
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return response
        logging.info(u'Call reportSignup interface end, courseId: %s',
                     course_id)
        return response

    def report_signup_package(self, user_id, user_id_type,
                              package_signup_info):
        """
        :param user_id:用户华为帐号ID
        :param user_id_type:user_id字段对应的帐号类型
        :param package_signup_info:相关类
        :return: response
        """
        logging.info('Call reportSignupPackage interface start')
        response = Response()
        try:
            url = ApiConstant.REPORT_SIGNUP_PACKAGE.format(
                user_id, user_id_type)
            http_common_response = HttpCommonResponse(
                self.__request_sender.put(
                    url=url, body=package_signup_info.to_json_string()))
            response.result = Helpers.build_result(
                http_common_response.get_rsp())
        except EduKitException as e:
            logging.error(
                u"Call reportSignupPackage interface failed. ErrorMessage: %s",
                str(e))
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return response
        logging.info('Call reportSignupPackage interface end')
        return response

    def batch_report_signup_course(self, user_id, user_id_type,
                                   batch_report_signup_course_request):
        """
        :param user_id:用户华为帐号ID
        :param user_id_type:user_id字段对应的帐号类型
        :param batch_report_signup_course_request:相关类
        :return: response
        """
        logging.info("Call reportSignupPackage interface start")
        response = Response()
        try:
            url = ApiConstant.BATCH_REPORT_SIGNUP_COURSE.format(
                user_id, user_id_type)
            http_common_response = \
                HttpCommonResponse(self.__request_sender.put(
                    url=url,
                    body=batch_report_signup_course_request.to_json_string()))
            response.result = Helpers.build_result(
                http_common_response.get_rsp())
        except EduKitException as e:
            logging.error(
                u"Call batchReportSignupCourse interface failed. "
                u"ErrorMessage: %s",
                str(e))
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return response
        logging.info("Call batchReportSignupCourse interface end")
        return response
