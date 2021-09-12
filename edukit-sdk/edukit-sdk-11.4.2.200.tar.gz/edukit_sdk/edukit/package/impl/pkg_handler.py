#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
import json
import logging

from edukit_sdk.edukit.common.constant.api_constant import ApiConstant
from edukit_sdk.edukit.common.constant.client_constant import ClientConstant
from edukit_sdk.edukit.common.constant.common_constant import CommonConstant
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.file_upload.file_upload import FileUpload
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.common.http.http_common_response import \
    HttpCommonResponse
from edukit_sdk.edukit.common.model.image_file_info import ImageFileInfo
from edukit_sdk.edukit.package.model.pkg import Pkg
from edukit_sdk.edukit.package.model.pkg_localized_data import PkgLocalizedData
from edukit_sdk.edukit.package.model.products import Products
from edukit_sdk.edukit.package.resp.pkg_common_response import \
    PkgCommonResponse
from edukit_sdk.edukit.package.resp.update_pkg_product_response import \
    UpdatePkgProductResponse
from edukit_sdk.edukit.package.resp.update_pkg_product_result import \
    UpdatePkgProductResult


class PkgHandler:
    def __init__(self, request_sender: EduKitRequestSender):
        self._request_sender = request_sender

    def create_pkg(self, pkg: Pkg):
        response = PkgCommonResponse()
        url = ApiConstant.CREATE_PKG_URL
        try:
            http_common_response = HttpCommonResponse(
                self._request_sender.post(url=url, body=pkg.to_json_string()))
            response = Helpers.parse_response(
                http_common_response.get_rsp(),
                'edukit_sdk.edukit.package.resp.pkg_common_response.'
                'PkgCommonResponse'
            )
        except EduKitException as e:
            logging.error('Create package failed. ErrorMessage: %s' % str(e))
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
        if response.result.result_code == CommonConstant.RESULT_SUCCESS:
            logging.info('Create package succeed, pkg_id:%s, pkg_edit_id:%s' %
                         (response.pkg_id, response.pkg_edit_id))
        else:
            logging.error('Create package failed, result:%s' %
                          response.result.to_string())
        return response

    def update_pkg(self, pkg_id, pkg: Pkg):
        response = PkgCommonResponse()
        url = ApiConstant.UPDATE_PKG_URL.format(pkg_id)
        try:
            http_common_response = HttpCommonResponse(
                self._request_sender.put(url=url, body=pkg.to_json_string()))
            response = Helpers.parse_response(
                http_common_response.get_rsp(),
                'edukit_sdk.edukit.package.resp.pkg_common_response.'
                'PkgCommonResponse'
            )
        except EduKitException as e:
            logging.error('Update package failed. ErrorMessage: %s' % str(e))
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
        logging.info('Update package succeed, pkg_id:%s, pkg_edit_id:%s' %
                     (response.pkg_id, response.pkg_edit_id))
        return response

    def delete_pkg(self, pkg_id):
        logging.info('Begin to delete package %s.' % pkg_id)
        url = ApiConstant.DELETE_PKG_URL.format(pkg_id)
        try:
            http_common_response = HttpCommonResponse(
                self._request_sender.delete(url=url))
            return Helpers.build_result(http_common_response.get_rsp())
        except EduKitException as e:
            logging.error('Delete package failed. ErrorMessage: %s' % str(e))
            return Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)

    def manage(self, pkg_id, action, removal_reason):
        logging.info('Begin to manage package %s.' % pkg_id)
        url = ApiConstant.MANAGE_PKG_STATUS_URL.format(pkg_id)
        body = {"action": action, "removalReason": removal_reason}
        body = bytes(json.dumps(body), encoding=ClientConstant.UTF_8)
        try:
            http_common_response = HttpCommonResponse(
                self._request_sender.post(url=url, body=body))
            return Helpers.build_result(http_common_response.get_rsp())
        except EduKitException as e:
            logging.error('Manage package failed. ErrorMessage: %s' % str(e))
            return Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)

    def update_pkg_product(self, pkg_id, pkg_product_list: Products):
        logging.info('Begin to update package product %s.' % pkg_id)
        update_pkg_product_rsp = UpdatePkgProductResponse()
        url = ApiConstant.UPDATE_PACKAGE_PRODUCT_URL.format(pkg_id)
        try:
            http_common_response = HttpCommonResponse(
                self._request_sender.put(
                    url=url, body=pkg_product_list.to_json_string()))
            result = http_common_response.get_rsp()
            update_pkg_product_rsp.result = Helpers.build_result(result)
        except EduKitException as e:
            logging.error('Update package product failed. ErrorMessage: %s' %
                          str(e))
            update_pkg_product_rsp.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return update_pkg_product_rsp

        if result['result']['resultCode'] != CommonConstant.RESULT_SUCCESS:
            return update_pkg_product_rsp

        details = list()
        for update_result in result['PkgProductUpdateResults']:
            update_pkg_product_result = UpdatePkgProductResult()
            update_pkg_product_result.dev_product_id = update_result[
                'devProductId']
            update_pkg_product_result.result = Helpers.build_result(
                update_result)
            details.append(update_pkg_product_result)

        update_pkg_product_rsp.details = details
        return update_pkg_product_rsp

    def delete(self, pkg_id, pkg_edit_id, product_id):
        logging.info(
            'Begin to delete package product, pdg_id:%s, pkg_edit_id:%s, '
            'product_id:%s.'
            % (pkg_id, pkg_edit_id, product_id))
        url = ApiConstant.DELETE_PACKAGE_PRODUCT_URL.format(
            pkg_id, pkg_edit_id, product_id)
        try:
            http_common_response = HttpCommonResponse(
                self._request_sender.delete(url=url))
            return Helpers.build_result(http_common_response.get_rsp())
        except EduKitException as e:
            logging.error('Delete package product failed. ErrorMessage: %s' %
                          str(e))
            return Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)

    def covert_localized_datas(self, pkg: Pkg):
        if not pkg.edit or not pkg.edit.localized_data:
            return

        for localized_data in pkg.edit.localized_data:
            result = self._covert_localized_data(localized_data)
            if not result:
                return

    def _covert_localized_data(self, localized_data: PkgLocalizedData):
        if localized_data.cover_image_info:
            upload_result = self._upload_image(localized_data.cover_image_info)
            if not upload_result:
                return False
            localized_data.cover_image_id = upload_result

        if not localized_data.introduce_infos:
            return

        introduce_ids = list()
        for introduce_info in localized_data.introduce_infos:
            upload_result = self._upload_image(introduce_info)
            if not upload_result:
                return False
            introduce_ids.append(upload_result)
        localized_data.introduce_ids = introduce_ids

    def _upload_image(self, image: ImageFileInfo):
        try:
            file_upload = FileUpload(path=image.path,
                                     resource_type=image.resource_type,
                                     request_sender=self._request_sender)
            result = file_upload.upload()
        except EduKitException as e:
            logging.error('Upload image:%s failed. ErrorMessage: %s' %
                          (image.path, str(e)))
            return False
        if not Helpers.is_success(result):
            logging.error('Upload image:%s failed. errMsg: %s' %
                          (image.path, result['result']['resultDesc']))
            return False

        return result['materialId']
