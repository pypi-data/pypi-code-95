#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.model.response import Response


class TeacherUpdateResponse(Response):
    def __init__(self):
        super(TeacherUpdateResponse, self).__init__()
        self._teacher_edit_id = None
        self._teacher_id = None
        self._create_new_edit_result = None
        self._update_basic_info_result = None
        self._update_metadata_result = None
        self._update_localized_data_result = None
        self._delete_localized_data_result = None
        self._teacher_commit_result = None

    @property
    def teacher_edit_id(self):
        return self._teacher_edit_id

    @teacher_edit_id.setter
    def teacher_edit_id(self, teacher_edit_id):
        self._teacher_edit_id = teacher_edit_id

    @property
    def teacher_id(self):
        return self._teacher_id

    @teacher_id.setter
    def teacher_id(self, teacher_id):
        self._teacher_id = teacher_id

    @property
    def create_new_edit_result(self):
        return self._create_new_edit_result

    @create_new_edit_result.setter
    def create_new_edit_result(self, create_new_edit_result):
        self._create_new_edit_result = create_new_edit_result

    @property
    def update_basic_info_result(self):
        return self._update_basic_info_result

    @update_basic_info_result.setter
    def update_basic_info_result(self, update_basic_info_result):
        self._update_basic_info_result = update_basic_info_result

    @property
    def update_metadata_result(self):
        return self._update_metadata_result

    @update_metadata_result.setter
    def update_metadata_result(self, update_metadata_result):
        self._update_metadata_result = update_metadata_result

    @property
    def update_localized_data_result(self):
        return self._update_localized_data_result

    @update_localized_data_result.setter
    def update_localized_data_result(self, update_localized_data_result):
        self._update_localized_data_result = update_localized_data_result

    @property
    def delete_localized_data_result(self):
        return self._delete_localized_data_result

    @delete_localized_data_result.setter
    def delete_localized_data_result(self, delete_localized_data_result):
        self._delete_localized_data_result = delete_localized_data_result

    @property
    def teacher_commit_result(self):
        return self._teacher_commit_result

    @teacher_commit_result.setter
    def teacher_commit_result(self, teacher_commit_result):
        self._teacher_commit_result = teacher_commit_result
