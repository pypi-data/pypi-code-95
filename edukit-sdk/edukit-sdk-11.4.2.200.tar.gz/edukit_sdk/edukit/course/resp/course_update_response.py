# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.model.response import Response


class CourseUpdateResponse(Response):
    def __init__(self):
        self._edit_id = None
        self._course_id = None
        self._commit_result = None
        self._create_new_course_edition_result = None
        self._update_product_price_result = None
        self._update_meta_data_result = None
        self._update_localized_data_result = None
        self._del_localized_data_result = None
        super(CourseUpdateResponse, self).__init__()

    @property
    def course_id(self):
        return self._course_id

    @course_id.setter
    def course_id(self, course_id):
        self._course_id = course_id

    @property
    def commit_result(self):
        return self._commit_result

    @commit_result.setter
    def commit_result(self, commit_result):
        self._commit_result = commit_result

    @property
    def create_new_course_edition_result(self):
        return self._create_new_course_edition_result

    @create_new_course_edition_result.setter
    def create_new_course_edition_result(self,
                                         create_new_course_edition_result):
        self._create_new_course_edition_result = \
            create_new_course_edition_result

    @property
    def update_product_price_result(self):
        return self._update_product_price_result

    @update_product_price_result.setter
    def update_product_price_result(self, update_product_price_result):
        self._update_product_price_result = update_product_price_result

    @property
    def update_meta_data_result(self):
        return self._update_meta_data_result

    @update_meta_data_result.setter
    def update_meta_data_result(self, update_meta_data_result):
        self._update_meta_data_result = update_meta_data_result

    @property
    def update_localized_data_result(self):
        return self._update_localized_data_result

    @update_localized_data_result.setter
    def update_localized_data_result(self, update_localized_data_result):
        self._update_localized_data_result = update_localized_data_result

    @property
    def del_localized_data_result(self):
        return self._del_localized_data_result

    @del_localized_data_result.setter
    def del_localized_data_result(self, del_localized_data_result):
        self._del_localized_data_result = del_localized_data_result

    @property
    def edit_id(self):
        return self._edit_id

    @edit_id.setter
    def edit_id(self, edit_id):
        self._edit_id = edit_id
