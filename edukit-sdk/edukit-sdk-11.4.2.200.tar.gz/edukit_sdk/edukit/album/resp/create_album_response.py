# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.model.response import Response


class CreateAlbumResponse(Response):
    def __init__(self):
        self._album_id = None
        self._edit_id = None
        self._edit_result = None
        self._success_import_course_num = None
        self._success_import_sub_album_num = None
        self._error_course_list = None
        self._error_sub_album_list = None
        self._result = None

    @property
    def edit_result(self):
        """
        :return:mixed
        """
        return self._edit_result

    @edit_result.setter
    def edit_result(self, edit_result):
        """
        :param edit_result:
        :return:
        """
        self._edit_result = edit_result

    @property
    def edit_id(self):
        """
        :return:mixed
        """
        return self._edit_id

    @edit_id.setter
    def edit_id(self, edit_id):
        """
        创建成功的Edit ID，后续调用接口更新专辑版本信息时，需要提供该ID
        :param edit_id:
        :return:
        """
        self._edit_id = edit_id

    @property
    def success_import_course_num(self):
        """
        :return:mixed
        """
        return self._success_import_course_num

    @success_import_course_num.setter
    def success_import_course_num(self, success_import_course_num):
        """
        成功导入的课程数量
        :param success_import_course_num:
        :return:
        """
        self._success_import_course_num = success_import_course_num

    @property
    def album_id(self):
        """
        :return:mixed
        """
        return self._album_id

    @album_id.setter
    def album_id(self, album_id):
        """
        创建成功的专辑ID
        :param album_id:
        :return:
        """
        self._album_id = album_id

    @property
    def success_import_sub_album_num(self):
        """
        :return:mixed
        """
        return self._success_import_sub_album_num

    @success_import_course_num.setter
    def success_import_sub_album_num(self, success_import_sub_album_num):
        """
        :param success_import_sub_album_num:
        :return:
        """
        self._success_import_sub_album_num = success_import_sub_album_num

    @property
    def error_course_list(self):
        """
        :return:mixed
        """
        return self._error_course_list

    @error_course_list.setter
    def error_course_list(self, error_course_list):
        """
        :param error_course_list:
        :return:
        """
        self._error_course_list = error_course_list

    @property
    def error_sub_album_list(self):
        """
        :return:mixed
        """
        return self._error_sub_album_list

    @error_course_list.setter
    def error_sub_album_list(self, error_sub_album_list):
        """
        :param error_sub_album_list:
        :return:
        """
        self._error_sub_album_list = error_sub_album_list

    @property
    def result(self):
        """
        :return:mixed
        """
        return self._result

    @result.setter
    def result(self, result):
        """
        :param result:
        :return:
        """
        self._result = result
