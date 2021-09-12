# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.model.response import Response


class UpdateAlbumResponse(Response):
    def __init__(self):
        self._result = None
        self._album_id = None
        self._edit_id = None
        self._edit_result = None
        self._delete_localized_result = None
        self._error_course_list = None
        self._error_sub_album_list = None

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

    @property
    def album_id(self):
        """
        :return:mixed
        """
        return self._album_id

    @album_id.setter
    def album_id(self, album_id):
        """
        更新成功的专辑ID
        :param album_id:
        :return:
        """
        self._album_id = album_id

    @property
    def edit_id(self):
        """
        :return:mixed
        """
        return self._edit_id

    @edit_id.setter
    def edit_id(self, edit_id):
        """
        更新成功的Edit ID，后续调用接口更新专辑版本信息时，需要提供该ID
        :param edit_id:
        :return:
        """
        self._edit_id = edit_id

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
    def delete_localized_result(self):
        """
        :return:mixed
        """
        return self._delete_localized_result

    @delete_localized_result.setter
    def delete_localized_result(self, delete_localized_result):
        """
        :param delete_localized_result:
        :return:
        """
        self._delete_localized_result = delete_localized_result

    @property
    def error_course_list(self):
        """
        :return:mixed
        """
        return self._error_course_list

    @error_course_list.setter
    def error_course_list(self, error_course_list):
        """
        添加失败的课程ID列表信息，最大2000个
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

    @error_sub_album_list.setter
    def error_sub_album_list(self, error_sub_album_list):
        """
        添加失败的子专辑列表信息，最大20个
        :param error_sub_album_list:
        :return:
        """
        self._error_sub_album_list = error_sub_album_list
