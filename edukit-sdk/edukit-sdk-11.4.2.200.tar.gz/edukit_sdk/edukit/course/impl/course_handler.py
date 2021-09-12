# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging

from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.constant.api_constant import ApiConstant
from edukit_sdk.edukit.common.exception.edu_kit_exception import \
    EduKitException
from edukit_sdk.edukit.common.constant.common_constant import CommonConstant
from edukit_sdk.edukit.common.constant.file_upload_constant import \
    FileUploadConstant
from edukit_sdk.edukit.common.file_upload.file_upload import FileUpload
from edukit_sdk.edukit.common.http.http_common_response import \
    HttpCommonResponse
from edukit_sdk.edukit.common.model.media_localized_data import \
    MediaLocalizedData
from edukit_sdk.edukit.common.model.response import Response
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.model.update_media_localized_data import \
    UpdateMediaLocalizedData
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.course.constant.course_constant import CourseConstant
from edukit_sdk.edukit.course.impl.change_course_status_request import \
    ChangeCourseStatusRequest
from edukit_sdk.edukit.course.impl.create_course_result import \
    CreateCourseResult
from edukit_sdk.edukit.course.impl.update_edit_localized_data import \
    UpdateEditLocalizedData
from edukit_sdk.edukit.course.impl.update_localized_data_request import \
    UpdateLocalizedDataRequest
from edukit_sdk.edukit.course.impl.update_product_price_request import \
    UpdateProductPriceRequest
from edukit_sdk.edukit.course.model.course import Course
from edukit_sdk.edukit.course.model.course_edit import CourseEdit
from edukit_sdk.edukit.course.model.course_localized_data import \
    CourseLocalizedData
from edukit_sdk.edukit.course.model.course_meta_data import CourseMetaData
from edukit_sdk.edukit.course.resp.course_status_response import \
    CourseStatusResponse
from edukit_sdk.edukit.course.resp.course_update_response import \
    CourseUpdateResponse


class CourseHandler:
    def __init__(self, request_sender: EduKitRequestSender):
        self._request_sender = request_sender

    def create_course(self):
        logging.info('Call Course createCourse interface start.')
        create_course_result = CreateCourseResult()
        try:
            url = ApiConstant.CREATE_COURSE_URL
            response = HttpCommonResponse(self._request_sender.post(url=url))
            create_course_result = Helpers.parse_response(
                response.get_rsp(), CourseConstant.CREATE_COURSE_RESULT)
        except EduKitException as e:
            logging.error(
                'Call course createCourse interface failed.error_message: %s' %
                e.message)
            create_course_result.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
        logging.info(
            'Call course createCourse interface end,and course_id: '
            '%s, edit_id: %s'
            % (create_course_result.course_id, create_course_result.edit_id))

        return create_course_result

    def update_course(self, course: Course,
                      create_course_result: CreateCourseResult):
        if course.course_meta_data:
            update_meta_data_result = self._update_meta_data(
                course.course_meta_data, create_course_result)
            if not update_meta_data_result:
                return False

        if course.course_multi_language_data_list:
            update_multi_language_data_list_result = \
                self._update_multi_language_data_list(
                    course, create_course_result)
            if not update_multi_language_data_list_result:
                return False

        if course.product_prices:
            update_product_prices_result = self._update_product_price(
                course.product_prices, create_course_result.course_id)
            if not update_product_prices_result:
                return False

        return True

    def update_course_edit(self, course_edit: CourseEdit,
                           create_course_result: CreateCourseResult):
        if not course_edit.course:
            return True

        if course_edit.course.course_meta_data:
            update_meta_data_result = self._update_meta_data(
                course_edit.course.course_meta_data, create_course_result)
            if not update_meta_data_result:
                return False

        if course_edit.course.course_multi_language_data_list:
            update_multi_language_data_list_result = \
                self._update_multi_language_data_list(
                    course_edit.course, create_course_result)
            if not update_multi_language_data_list_result:
                return False

        if course_edit.course.language_list_to_delete:
            del_course_localized_data_result = self._del_course_localized_data(
                course_edit.course, create_course_result)
            if not del_course_localized_data_result:
                return False

        if course_edit.course.product_prices:
            update_product_prices_result = self._update_product_price(
                course_edit.course.product_prices,
                create_course_result.course_id)
            if not update_product_prices_result:
                return False

        return True

    def _update_meta_data(self, course_meta_data: CourseMetaData,
                          create_course_result: CreateCourseResult):
        logging.info(
            'Call course updateMetaData interface start and '
            'course_id:%s, edit_id:%s'
            % (create_course_result.course_id, create_course_result.edit_id))
        try:
            url = ApiConstant.UPDATE_META_COURSE_URL.format(
                create_course_result.course_id, create_course_result.edit_id)
            update_meta_data_response = HttpCommonResponse(
                self._request_sender.put(url=url,
                                         body=course_meta_data.to_bytes()))
        except EduKitException as e:
            logging.error(
                'Call course updateMetaData interface failed and '
                'course_id:%s, edit_id:%s, error_message:%s'
                % (create_course_result.course_id,
                   create_course_result.edit_id, e.message))
            return False

        if not Helpers.is_success(update_meta_data_response.get_rsp()):
            result = update_meta_data_response.get_rsp()
            logging.error(
                'Call course updateMetaData interface failed and '
                'course_id:%s,edit_id:%s,error_message:%s,resultCode:'
                '%s' %
                (create_course_result.course_id, create_course_result.edit_id,
                 result.get(CourseConstant.RESULT).get(
                     CourseConstant.RESULT_DESC),
                 result.get(CourseConstant.RESULT).get(
                     CourseConstant.RESULT_CODE)))
            return False

        logging.info('Call course updateMetaData interface end')
        return True

    def _update_multi_language_data_list(
            self, course: Course, create_course_result: CreateCourseResult):
        # 包含课程章节 课程视频文件、课程音频文件,给出warnning
        self._course_media_type_warning(course)

        logging.info(
            'Call course updateLocalizedData interface start when updating '
            'course localizedData and course_id:%s, edit_'
            'id:%s' %
            (create_course_result.course_id, create_course_result.edit_id))
        update_flag = True
        for course_multi_language_data in \
                course.course_multi_language_data_list:
            update_localized_data_request = UpdateLocalizedDataRequest()
            if course_multi_language_data and \
                    course_multi_language_data.course_localized_data:
                localized_data_result = self._upload_localized_data(
                    course_multi_language_data.course_localized_data)
                if not localized_data_result:
                    return False
                update_localized_data_request.localized_data = \
                    localized_data_result

            if course_multi_language_data and \
                    course_multi_language_data.media_localized_data_list:
                upload_media_data_result_list = list()
                update_flag = True
                for media_localized_data in \
                        course_multi_language_data.media_localized_data_list:
                    single_result = self.upload_media_localized_data(
                        media_localized_data)
                    if not single_result:
                        update_flag = False
                        break
                    upload_media_data_result_list.append(single_result)

                if update_flag:
                    update_localized_data_request.localized_media = \
                        upload_media_data_result_list

            try:
                url = ApiConstant.UPDATE_LOCALIZED_COURSE_URL.format(
                    create_course_result.course_id,
                    create_course_result.edit_id,
                    course_multi_language_data.language)
                response = HttpCommonResponse(
                    self._request_sender.put(
                        url=url,
                        body=update_localized_data_request.to_bytes()))
                if not Helpers.is_success(response.get_rsp()):
                    result = response.get_rsp()
                    logging.error(
                        'Call course updateLocalizedData interface failed '
                        'and course_id:%s, edit_id:%s, error_message:'
                        ' %s, resultCode: %s' %
                        (create_course_result.course_id,
                         create_course_result.edit_id,
                         result.get(CourseConstant.RESULT).get(
                             CourseConstant.RESULT_DESC),
                         result.get(CourseConstant.RESULT).get(
                             CourseConstant.RESULT_CODE)))
                    update_flag = False
                    break
            except EduKitException as e:
                logging.error(
                    'Call course updateLocalizedData interface failed and '
                    'course_id:%s, edit_id:%s, error_message: %s'
                    % (create_course_result.course_id,
                       create_course_result.edit_id, e.message))
                update_flag = False
                break

        logging.info(
            'Call course updateLocalizedData interface end and '
            'course_id:%s, edit_id:%s'
            % (create_course_result.course_id, create_course_result.edit_id))
        return update_flag

    def _del_course_localized_data(self, course: Course,
                                   create_course_result: CreateCourseResult):
        del_flag = True
        for language in course.language_list_to_delete:
            logging.info(
                'Call course deleteLocalizedData interface start and '
                'course_id:%s,edit_id:%s,language:%s'
                % (create_course_result.course_id,
                   create_course_result.edit_id, language))
            try:
                url = ApiConstant.DELETE_COURSE_URL.format(
                    create_course_result.course_id,
                    create_course_result.edit_id, language)
                response = HttpCommonResponse(
                    self._request_sender.delete(url=url))
                if not Helpers.is_success(response.get_rsp()):
                    result = response.get_rsp()
                    logging.error(
                        'Call course deleteLocalizedData interface failed and '
                        'course_id:%s, edit_id:%s, language:%s, '
                        'errormessage: %s, errorCode: %s' %
                        (create_course_result.course_id,
                         create_course_result.edit_id, language,
                         result.get(CourseConstant.RESULT).get(
                             CourseConstant.RESULT_DESC),
                         result.get(CourseConstant.RESULT).get(
                             CourseConstant.RESULT_CODE)))
                    del_flag = False
                    break
            except EduKitException as e:
                logging.error(
                    'Call course deleteLocalizedData interface failed and '
                    'course_id:%s, edit_id:%s, language:%s, error'
                    'message:%s, errorCode:%s' %
                    (create_course_result.course_id,
                     create_course_result.edit_id, language, e.message,
                     e.code))
                del_flag = False
                break
            logging.info(
                'Call course deleteLocalizedData interface end and '
                'course_id:%s,edit_id:%s,language:%s'
                % (create_course_result.course_id,
                   create_course_result.edit_id, language))

        return del_flag

    def _course_media_type_warning(self, course: Course):
        if not course.course_meta_data:
            return
        if not course.course_meta_data.meta_data:
            return
        if not course.course_meta_data.meta_data.include_lessons:
            return

        multi_language_data_list = course.course_multi_language_data_list
        for multi_language_data in multi_language_data_list:
            if multi_language_data.media_localized_data_list:
                for media_localized_data in \
                        multi_language_data.media_localized_data_list:
                    if self._is_audio_or_video_file(media_localized_data):
                        logging.warning(
                            'Course video or audio(mediaType is 2 or 3) is '
                            'not needed when the course includes lessons.')
                        break

    @staticmethod
    def _is_audio_or_video_file(media_localized_data: MediaLocalizedData):
        return media_localized_data.media_type in (
            CommonConstant.MEDIA_TYPE.get(CourseConstant.COURSE_AUDIO_FILE),
            CommonConstant.MEDIA_TYPE.get(CourseConstant.COURSE_VIDEO_FILE))

    def _upload_localized_data(self,
                               course_localized_data: CourseLocalizedData):
        edit_localized_data = UpdateEditLocalizedData()
        edit_localized_data.name = course_localized_data.name
        edit_localized_data.short_description = \
            course_localized_data.short_description
        edit_localized_data.full_description = \
            course_localized_data.full_description
        edit_localized_data.deeplink_url = course_localized_data.deeplink_url
        if course_localized_data:
            upload_cover_img_result = self._upload_cover_image(
                course_localized_data)
            if not upload_cover_img_result:
                return False

            if isinstance(upload_cover_img_result, str):
                edit_localized_data.cover_id = upload_cover_img_result

            upload_portrait_img_result = self._upload_portrait_image(
                course_localized_data)
            if not upload_portrait_img_result:
                return False
            if isinstance(upload_portrait_img_result, str):
                edit_localized_data.portrait_cover_id = \
                    upload_portrait_img_result

            upload_introduce_img_result = self._upload_introduce_image(
                course_localized_data)
            if not isinstance(upload_introduce_img_result,
                              dict) and not upload_introduce_img_result:
                logging.error('Upload introduceImage failed.')
                return False

            if isinstance(upload_introduce_img_result, list):
                edit_localized_data.introduce_ids = upload_introduce_img_result

        return edit_localized_data

    def off_shelf(self, course: Course):
        if not course or not course.course_id:
            logging.error('CourseId can not be empty when offShelf course.')
            return Helpers.build_error_result(
                CommonErrorCode.INVALID_COURSE_PARAMS)
        course_id = course.course_id
        logging.info('OffShelf course start and course_id: %s' % course_id)
        response = Response()
        try:
            url = ApiConstant.REMOVE_COURSE_URL.format(course_id)
            body = None
            if course.change_course_status_data:
                body = course.change_course_status_data.to_bytes()
            http_common_response = HttpCommonResponse(
                self._request_sender.put(url=url, body=body))
        except EduKitException as e:
            logging.error(
                'Call offShelf course interface failed and '
                'course_id:%s,error_message:%s'
                % (course_id, e.message))
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return response
        if not Helpers.is_success(http_common_response.get_rsp()):
            result = http_common_response.get_rsp()
            logging.error(
                'Call offShelf course interface failed.course_id:%s,'
                'error_message:%s'
                % (course_id, result.get(CourseConstant.RESULT).get(
                    CourseConstant.RESULT_DESC)))
            response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return response

        logging.info(
            'OffShelf course end and result: %s' %
            Helpers.build_result(http_common_response.get_rsp()).to_string())
        response.result = Helpers.build_result(http_common_response.get_rsp())
        return response

    def get_course_status(self, course_id):
        if not course_id:
            logging.error('CourseId can not be empty')
            return Helpers.build_error_result(
                CommonErrorCode.INVALID_COURSE_PARAMS)
        logging.info(
            'Call course getCourseStatus interface start,and course_id: %s' %
            course_id)
        course_status_response = CourseStatusResponse()
        try:
            url = ApiConstant.GET_COURSE_STATUS_URL.format(course_id)
            response = HttpCommonResponse(self._request_sender.get(url=url))
            if response.get_rsp() and response.get_rsp().get(
                    'result') and response.get_rsp().get('result').get(
                        'resultCode') != CommonConstant.RESULT_SUCCESS:
                result = response.get_rsp()
                logging.error(
                    'Call course getCourseStatus interface failed.'
                    'course_id:%s,error_message:%s' %
                    (course_id, result.get(
                        CourseConstant.RESULT).get(
                        CourseConstant.RESULT_DESC)))
                course_status_response.result = Helpers.build_error_result(
                    CommonErrorCode.CALL_API_INTERFACE_FAILED)
                return course_status_response
            course_status_response = Helpers.parse_response(
                response.get_rsp(), CourseConstant.COURSE_STATUS_RESPONSE)
        except EduKitException as e:
            logging.error(
                'Call course getCourseStatus interface failed and '
                'course_id:%s, errorMsg:%s.'
                % (course_id, e.message))
            course_status_response.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return course_status_response

        logging.info('Call course getCourseStatus interface end')
        course_status_response.result = Helpers.build_error_result(
            CommonErrorCode.SUCCESS)
        return course_status_response

    def upload_media_localized_data(self,
                                    media_localized_data: MediaLocalizedData):
        update_media_localized_data = UpdateMediaLocalizedData()
        update_media_localized_data.media_type = \
            media_localized_data.media_type
        update_media_localized_data.height = media_localized_data.height
        update_media_localized_data.width = media_localized_data.width
        update_media_localized_data.media_len = media_localized_data.media_len
        update_media_localized_data.ordinal = media_localized_data.ordinal

        upload_frame_img_result = self._upload_frame_image(
            media_localized_data)
        if not upload_frame_img_result:
            return False
        if isinstance(upload_frame_img_result, str):
            update_media_localized_data.frame_id = upload_frame_img_result

        upload_media_result = self._upload_media(media_localized_data)
        if not upload_media_result:
            return False
        if isinstance(upload_media_result, dict):
            update_media_localized_data.meida_id = upload_media_result.get(
                CourseConstant.MATERIAL_Id)
            update_media_localized_data.file_name = Helpers.get_file_base_name(
                upload_media_result.get(CourseConstant.PATH))
            update_media_localized_data.size = Helpers.get_file_size(
                upload_media_result.get(CourseConstant.PATH))
            update_media_localized_data.sha256 = Helpers.get_sha256(
                upload_media_result.get(CourseConstant.PATH))

        return update_media_localized_data

    def _upload_cover_image(self, course_localized_data: CourseLocalizedData):
        if not course_localized_data.cover_image_file_info:
            return True
        try:
            file_upload = FileUpload(
                path=course_localized_data.cover_image_file_info.path,
                resource_type=FileUploadConstant.RESOURCE_TYPE[
                    CourseConstant.COURSE_PACKAGE_HORIZONTAL_COVER],
                request_sender=self._request_sender)
            result = file_upload.upload()
        except EduKitException as e:
            logging.error('Upload horizon cover image failed. errMsg:%s' %
                          e.message)
            return False

        if not Helpers.is_success(result):
            logging.error('Upload horizon cover image failed. errMsg:%s' %
                          result.get(CourseConstant.RESULT).get(
                              CourseConstant.RESULT_DESC))
            return False

        return result.get('materialId')

    def _upload_portrait_image(self,
                               course_localized_data: CourseLocalizedData):
        if not course_localized_data.portrait_cover_image_file_info:
            return True

        try:
            file_upload = FileUpload(
                path=course_localized_data.portrait_cover_image_file_info.path,
                resource_type=FileUploadConstant.RESOURCE_TYPE[
                    CourseConstant.COURSE_PORTRAIT_COVER],
                request_sender=self._request_sender)
            result = file_upload.upload()
        except EduKitException as e:
            logging.error('Upload portrait image failed. errMsg:%s' %
                          e.message)
            return False

        if not Helpers.is_success(result):
            logging.error('Upload portrait image failed. errMsg:%s' %
                          result.get(CourseConstant.RESULT).get(
                              CourseConstant.RESULT_DESC))
            return False

        return result.get(CourseConstant.MATERIAL_Id)

    def _upload_introduce_image(self,
                                course_localized_data: CourseLocalizedData):
        if not course_localized_data.introduce_image_file_infos:
            return True

        material_id_list = list()
        for introduce_image_file_info in \
                course_localized_data.introduce_image_file_infos:
            try:
                file_upload = FileUpload(
                    path=introduce_image_file_info.path,
                    resource_type=FileUploadConstant.RESOURCE_TYPE[
                        CourseConstant.COURSE_PACKAGE_INTRODUCTION],
                    request_sender=self._request_sender)
                result = file_upload.upload()
            except EduKitException:
                return False

            if not Helpers.is_success(result):
                logging.error('Upload introduce image failed. errMsg:%s' %
                              result.get(CourseConstant.RESULT).get(
                                  CourseConstant.RESULT_DESC))
                return False

            material_id_list.append(result.get(CourseConstant.MATERIAL_Id))

        return material_id_list

    def _upload_frame_image(self, media_localized_data: MediaLocalizedData):
        if not media_localized_data.frame_image_file_info:
            return True

        try:
            file_upload = FileUpload(
                path=media_localized_data.frame_image_file_info.path,
                resource_type=FileUploadConstant.RESOURCE_TYPE[
                    CourseConstant.PROMOTIONAL_VIDEO_POSTER],
                request_sender=self._request_sender)
            result = file_upload.upload()
        except EduKitException as e:
            logging.error('Upload frame image failed. errMsg: %s' % e.message)
            return False

        if not Helpers.is_success(result):
            logging.error('Upload frame image failed. errMsg: %s' % result.get(
                CourseConstant.RESULT).get(CourseConstant.RESULT_DESC))
            return False

        return result.get(CourseConstant.MATERIAL_Id)

    def _upload_media(self, media_localized_data: MediaLocalizedData):
        if not media_localized_data.media_file_info:
            return True
        public_file = False
        if media_localized_data.media_type is CommonConstant.MEDIA_TYPE.get(
                CourseConstant.COURSE_INTRODUCTION_VIDEO):
            public_file = True

        try:
            file_upload = FileUpload(
                path=media_localized_data.media_file_info.path,
                file_type=media_localized_data.media_file_info.file_type,
                public_file=public_file,
                request_sender=self._request_sender)
            result = file_upload.upload()
        except EduKitException as e:
            logging.error('Upload media failed. errMsg: %s' % e.message)
            return False

        if not Helpers.is_success(result):
            logging.error('Upload media failed. errMsg: %s' % result.get(
                CourseConstant.RESULT).get(CourseConstant.RESULT_DESC))
            return False

        return {
            CourseConstant.PATH: media_localized_data.media_file_info.path,
            CourseConstant.MATERIAL_Id: result.get(CourseConstant.MATERIAL_Id)
        }

    def _update_product_price(self, produce_prices, course_id):
        logging.info(
            'Call course updateProductPrice interface start and course_id:%s' %
            course_id)
        try:
            update_product_price_request = UpdateProductPriceRequest()
            update_product_price_request.product_prices = produce_prices
            url = ApiConstant.UPDATE_PRICE_COURSE_URL.format(course_id)
            response = HttpCommonResponse(
                self._request_sender.put(
                    url=url, body=update_product_price_request.to_bytes()))
        except EduKitException as e:
            logging.error(
                'Call course updateProductPrice interface failed and '
                'course_id:%s, error_message:%s'
                % (course_id, e.message))
            return False

        if not Helpers.is_success(response.get_rsp()):
            result = response.get_rsp()
            logging.error(
                'Call course updateProductPrice interface failed and '
                'course_id:%s, error_message:%s, resultCode:%s'
                % (course_id, result.get(CourseConstant.RESULT).get(
                    CourseConstant.RESULT_DESC),
                   result.get(CourseConstant.RESULT).get(
                       CourseConstant.RESULT_CODE)))
            return False

        logging.info('Call course updateProductPrice interface end')
        return True

    def commit_course(self, course_id, edit_id, course: Course,
                      change_course_status_request: ChangeCourseStatusRequest):
        logging.info(
            'Call course commit_course interface start and course_id:%s, '
            'edit_id:%s'
            % (course_id, edit_id))
        try:
            if course.change_course_status_data and \
                    course.change_course_status_data.remarks:
                change_course_status_request.remarks = \
                    course.change_course_status_data.remarks
            if course.change_course_status_data and \
                    course.change_course_status_data.removal_reason:
                change_course_status_request.removal_reason = \
                    course.change_course_status_data.removal_reason
            url = ApiConstant.COMMIT_COURSE_URL.format(course_id, edit_id)
            response = HttpCommonResponse(
                self._request_sender.put(
                    url=url, body=change_course_status_request.to_bytes()))
        except EduKitException as e:
            logging.error(
                'Call course commit_course interface failed and course_id:%s, '
                'edit_id:%s, error_message: %s'
                % (course_id, edit_id, e.message))

            return Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)

        if not Helpers.is_success(response.get_rsp()):
            result = response.get_rsp()
            logging.error(
                'Call course commit_course interface failed and course_id:%s, '
                'edit_id:%s, error_message: %s, result_'
                'code'
                ': %s' % (course_id, edit_id, result.get(
                    CourseConstant.RESULT).get(CourseConstant.RESULT_DESC),
                    result.get(CourseConstant.RESULT).get(
                    CourseConstant.RESULT_CODE)))

            return Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)

        logging.info('Call course commit_course interface end.')
        return Helpers.build_error_result(CommonErrorCode.SUCCESS)

    def create_new_course_edit(self, course_edit: CourseEdit):
        course_id = None
        if course_edit.course and course_edit.course.course_id:
            course_id = course_edit.course.course_id
        update_course = CourseUpdateResponse()
        if not course_id:
            logging.error(
                'CourseId can not be null when create a new course edition.')
            update_course.result = Helpers.build_error_result(
                CommonErrorCode.INVALID_COURSE_PARAMS)
            return update_course
        try:
            logging.info(
                'Call createCourseEdit interface start and course_id:%s' %
                course_id)
            url = ApiConstant.CREATE_NEW_COURSE_EDIT_URL.format(course_id)
            response = HttpCommonResponse(self._request_sender.post(url=url))
            create_course_result = Helpers.parse_response(
                response.get_rsp(), CourseConstant.CREATE_COURSE_RESULT)
            update_course.course_id = course_id
            update_course.edit_id = create_course_result.edit_id
            update_course.result = create_course_result.result
            logging.info(
                'Call createCourseEdit interface end and resultCode:%s,:'
                'error_message%s'
                % (create_course_result.result.result_desc,
                   create_course_result.result.result_code))

            return update_course
        except EduKitException as e:
            logging.error(
                'Call createCourseEdit interface failed and course_id:%s, '
                'error_message:%s, resultCode:%s'
                % (course_id, e.message, e.code))
            update_course.result = Helpers.build_error_result(
                CommonErrorCode.CALL_API_INTERFACE_FAILED)
            return update_course
