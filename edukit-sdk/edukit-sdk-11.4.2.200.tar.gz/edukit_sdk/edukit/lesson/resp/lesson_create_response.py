# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.model.response import Response


class LessonCreateResponse(Response):
    def __init__(self):
        self._lesson_id = None
        self._lesson_edit_id = None
        self._update_lesson_meta_data_result = None
        self._update_localized_data_result = None
        super(LessonCreateResponse, self).__init__()

    @property
    def lesson_id(self):
        """
        :return:mixed
        """
        return self._lesson_id

    @lesson_id.setter
    def lesson_id(self, lesson_id):
        """
        :param lesson_id:
        """
        self._lesson_id = lesson_id

    @property
    def update_localized_data_result(self):
        """
        :return: mixed
        """
        return self._update_localized_data_result

    @update_localized_data_result.setter
    def update_localized_data_result(self, update_localized_data_result):
        """
        :param update_localized_data_result:
        """
        self._update_localized_data_result = update_localized_data_result

    @property
    def update_lesson_meta_data_result(self):
        """
        :return:mixed
        """
        return self._update_lesson_meta_data_result

    @update_lesson_meta_data_result.setter
    def update_lesson_meta_data_result(self, update_lesson_meta_data_result):
        """
        :param update_lesson_meta_data_result:
        """
        self._update_lesson_meta_data_result = update_lesson_meta_data_result

    @property
    def lesson_edit_id(self):
        """
        :return:mixed
        """
        return self._lesson_edit_id

    @lesson_edit_id.setter
    def lesson_edit_id(self, lesson_edit_id):
        """
        :param lesson_edit_id:
        """
        self._lesson_edit_id = lesson_edit_id
