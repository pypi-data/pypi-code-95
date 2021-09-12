# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.common.model.response import Response
from edukit_sdk.edukit.signup.impl.signup_handler import SignupHandler


class SignupRequest:
    @staticmethod
    def report_signup(user_id, course_id, user_id_type, signup_info,
                      credential_list):
        """
        :param user_id:用户ID
        :param course_id:课程ID
        :param user_id_type:user_id字段对应的帐号类型
        :param signup_info:相关类
        :param credential_list:用户凭据
        :return:
        """
        response = Response()

        if Helpers.has_empty_param(
            [
                user_id,
                course_id,
                user_id_type,
                signup_info,
                credential_list]):
            response.result = Helpers.build_error_result(
                CommonErrorCode.PARAM_CANNOT_BE_EMPTY)
            return response
        signup_handler = SignupHandler(EduKitRequestSender(credential_list))
        return signup_handler.report_signup(user_id, course_id, user_id_type,
                                            signup_info)

    @staticmethod
    def report_signup_package(user_id, user_id_type, package_signup_info,
                              credential_list):
        """
        :param user_id:用户ID
        :param user_id_type:user_id字段对应的帐号类型
        :param package_signup_info:相关类
        :param credential_list:用户凭据
        :return:
        """
        response = Response()
        if Helpers.has_empty_param(
            [
                user_id,
                user_id_type,
                package_signup_info
            ]
        ):
            response.result = Helpers.build_error_result(
                CommonErrorCode.PARAM_CANNOT_BE_EMPTY)
            return response
        signup_handler = SignupHandler(EduKitRequestSender(credential_list))
        return signup_handler.report_signup_package(
            user_id,
            user_id_type,
            package_signup_info
        )

    @staticmethod
    def batch_report_signup_course(
            user_id,
            user_id_type,
            batch_report_signup_course_request,
            credential_list
    ):
        """
        :param user_id:用户ID
        :param user_id_type:user_id字段对应的帐号类型
        :param batch_report_signup_course_request:相关类
        :param credential_list:用户凭据
        :return:
        """
        response = Response()
        if Helpers.has_empty_param(
            [
                user_id,
                user_id_type,
                batch_report_signup_course_request
            ]
        ):
            response.result = Helpers.build_error_result(
                CommonErrorCode.PARAM_CANNOT_BE_EMPTY)
            return response
        signup_handler = SignupHandler(EduKitRequestSender(credential_list))
        return signup_handler.batch_report_signup_course(
            user_id,
            user_id_type,
            batch_report_signup_course_request
        )
