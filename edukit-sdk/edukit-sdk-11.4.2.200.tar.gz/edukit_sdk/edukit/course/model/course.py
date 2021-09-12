# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.course.model.change_course_status_data import \
    ChangeCourseStatusData
from edukit_sdk.edukit.course.model.course_meta_data import CourseMetaData


class Course:
    def __init__(self):
        self._course_id = None
        self._course_meta_data = None
        self._course_multi_language_data_list = None
        self._language_list_to_delete = None
        self._product_prices = None
        self._change_course_status_data = None
        self._progress_callback = None

    @property
    def course_id(self):
        """
        :return: mixed
        """
        return self._course_id

    @course_id.setter
    def course_id(self, course_id):
        """
        课程id
        :param course_id:
        :return:
        """
        self._course_id = course_id

    @property
    def course_meta_data(self):
        """
        :return: mixed
        """
        return self._course_meta_data

    @course_meta_data.setter
    def course_meta_data(self, course_meta_data: CourseMetaData):
        """
        课程元数据
        :param course_meta_data:
        :return:
        """
        self._course_meta_data = course_meta_data

    @property
    def course_multi_language_data_list(self):
        """
        :return: mixed
        """
        return self._course_multi_language_data_list

    @course_multi_language_data_list.setter
    def course_multi_language_data_list(self, course_multi_language_data_list):
        """
         课程本地化多语言数据列表
        :param course_multi_language_data_list:
        :return:
        """
        self._course_multi_language_data_list = course_multi_language_data_list

    @property
    def language_list_to_delete(self):
        """
        :return:mixed
        """
        return self._language_list_to_delete

    @language_list_to_delete.setter
    def language_list_to_delete(self, language_list_to_delete):
        """
        待删除的本地化多语言数据语言列表
        :param language_list_to_delete:
        :return:
        """
        self._language_list_to_delete = language_list_to_delete

    @property
    def product_prices(self):
        """
        :return: mixed
        """
        return self._product_prices

    @product_prices.setter
    def product_prices(self, product_prices):
        """
        课程定价列表
        :param product_prices:
        :return:
        """
        self._product_prices = product_prices

    @property
    def change_course_status_data(self):
        """
        :return: mixed
        """
        return self._change_course_status_data

    @change_course_status_data.setter
    def change_course_status_data(
            self, change_course_status_data: ChangeCourseStatusData):
        """
        changeCourseStatus请求消息体
        :param change_course_status_data:
        :return:
        """
        self._change_course_status_data = change_course_status_data

    @property
    def progress_callback(self):
        """
        :return: mixed
        """
        return self._progress_callback

    @progress_callback.setter
    def progress_callback(self, progress_callback):
        """
        文件上传进度回调函数
        :param progress_callback:
        :return:
        """
        self._progress_callback = progress_callback
