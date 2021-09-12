# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging

from edukit_sdk.edukit.catalogue.constant.catalogue_constant import \
    CatalogueConstant
from edukit_sdk.edukit.catalogue.model.catalogue import Catalogue
from edukit_sdk.edukit.catalogue.model.catalogue_edit_data import \
    CatalogueEditData
from edukit_sdk.edukit.catalogue.resp.create_catalogue_response import \
    CreateCatalogueResponse
from edukit_sdk.edukit.catalogue.resp.update_catalogue_response import \
    UpdateCatalogueResponse
from edukit_sdk.edukit.common.constant.api_constant import ApiConstant
from edukit_sdk.edukit.common.constant.common_constant import CommonConstant
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.common.http.http_common_response import \
    HttpCommonResponse


class CatalogueHandler:
    def __init__(self, request_sender: EduKitRequestSender):
        self._request_sender = request_sender

    def create_catalogue(self, catalogue_edit_data: CatalogueEditData,
                         course_id, course_edit_id):
        logging.info('Call create_catalogue interface start.')
        create_catalogue_response = CreateCatalogueResponse()
        try:
            url = ApiConstant.CREATE_CATALOGUE_URL.format(
                course_id, course_edit_id)
            body = catalogue_edit_data.to_bytes()
            response = HttpCommonResponse(
                self._request_sender.post(url=url, body=body))
            create_catalogue_response = Helpers.parse_response(
                response.get_rsp(),
                CatalogueConstant.CREATE_CATALOGUE_RESPONSE)
            if create_catalogue_response and \
                    create_catalogue_response.result and \
                    create_catalogue_response.result.result_code \
                    != CommonConstant.RESULT_SUCCESS:
                result = create_catalogue_response.result
                logging.error(
                    'Call create_catalogue interface failed resultCode:'
                    '%s error_message:%s'
                    % (result.result_code, result.result_desc))
                return create_catalogue_response
        except EduKitException as e:
            logging.error(
                'Call create_catalogue interface failed. errorMessage:%s' %
                e.message)
            create_catalogue_response.result = Helpers\
                .build_error_result(CommonErrorCode.CALL_API_INTERFACE_FAILED)
        logging.info(
            'Call createCatalogue interface end, and '
            'catalogueId: %s, catalogueEditId: %s'
            % (create_catalogue_response.catalogue_id,
               create_catalogue_response.catalogue_edit_id))
        return create_catalogue_response

    def update_catalogue(self, catalogue: Catalogue, course_id,
                         course_edit_id):
        logging.info('Call update_catalogue interface start.')
        update_catalogue_response = UpdateCatalogueResponse()
        try:
            url = ApiConstant.UPDATE_CATALOGUE_URL.format(
                course_id, course_edit_id, catalogue.catalogue_id)
            body = catalogue.catalogue_edit.to_bytes()
            response = HttpCommonResponse(
                self._request_sender.put(url=url, body=body))
            update_catalogue_response = Helpers.parse_response(
                response.get_rsp(),
                CatalogueConstant.UPDATE_CATALOGUE_RESPONSE)
            result = update_catalogue_response.result
            if result and result.result_code \
                    != CommonConstant.RESULT_SUCCESS:
                logging.info(
                    'Call update_catalogue interface failed '
                    'and code: %s message: %s'
                    % (result.result_code, result.result_desc))
                return update_catalogue_response
        except EduKitException as e:
            logging.error(
                'Call updateCatalogue interface failed. errorMessage:%s' %
                e.message)
            update_catalogue_response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
        logging.info(
            'Call update_catalogue interface end, and catalogueEditId: %s' %
            update_catalogue_response.catalogue_edit_id)
        return update_catalogue_response

    def delete_catalogue(self, course_id, course_edit_id, catalogue_id):
        logging.info('Call delete_catalogue interface start.')
        try:
            url = ApiConstant.DELETE_CATALOGUE_URL.format(
                course_id, course_edit_id, catalogue_id)
            response = HttpCommonResponse(self._request_sender.delete(url=url))
            result = response.get_rsp()
            if not Helpers.is_success(result):
                logging.info(
                    'Call delete catalogue interface failed and code: %s '
                    'message: %s'
                    % (result.get(CatalogueConstant.RESULT).get(
                        CatalogueConstant.RESULT_CODE),
                       result.get(CatalogueConstant.RESULT).get(
                           CatalogueConstant.RESULT_DESC)))
                return Helpers.build_error_result(
                    CommonErrorCode.CALL_API_INTERFACE_FAILED)
            logging.info(
                'Call delete catalogue interface end. catalogueId: %s' %
                catalogue_id)
            return Helpers.build_result(result)
        except EduKitException as e:
            logging.error(
                'Call delete Catalogue interface failed. errorMessage:%s' %
                e.message)
            return Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
