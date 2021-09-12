#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.teacher.model.teacher_metadata import TeacherMetaData


class Teacher:
    def __init__(self):
        self._teacher_id = None
        self._dev_teacher_id = None
        self._teacher_metadata = None
        self._teacher_multi_language_data_list = None
        self._language_list_to_delete = None

    @property
    def teacher_id(self):
        """
        :return: mixed
        """
        return self._teacher_id

    @teacher_id.setter
    def teacher_id(self, teacher_id):
        """
        教师ID,通过addTeacher接口返回
        :param teacher_id:
        :return:
        """
        self._teacher_id = teacher_id

    @property
    def dev_teacher_id(self):
        """
        :return: mixed
        """
        return self._dev_teacher_id

    @dev_teacher_id.setter
    def dev_teacher_id(self, dev_teacher_id):
        """
        教师编号初值或待更新值，由开发者指定
        :param dev_teacher_id:
        :return:
        """
        self._dev_teacher_id = dev_teacher_id

    @property
    def teacher_metadata(self):
        """
        :return: mixed
        """
        return self._teacher_metadata

    @teacher_metadata.setter
    def teacher_metadata(self, teacher_metadata: TeacherMetaData):
        """
        教师元数据，
        包含两个字段，famousFlag和defaultLang。
        您必须提供默认语言对应的教师信息
        此字段在教师信息首次提交审核时必须指定，否则将返回错误；后续更新时可不携带，此时将保持当前取值不变
        :param teacher_metadata:
        :return:
        """
        self._teacher_metadata = teacher_metadata

    @property
    def teacher_multi_language_data_list(self):
        """
        :return: mixed
        """
        return self._teacher_multi_language_data_list

    @teacher_multi_language_data_list.setter
    def teacher_multi_language_data_list(self,
                                         teacher_multi_language_data_list):
        """
        教师本地多语言数据(详见TeacherMultiLangLocalizedData类)的List
        :param teacher_multi_language_data_list:
        :return:
        """
        self._teacher_multi_language_data_list = \
            teacher_multi_language_data_list

    @property
    def language_list_to_delete(self):
        """
        :return: mixed
        """
        return self._language_list_to_delete

    @language_list_to_delete.setter
    def language_list_to_delete(self, language_list_to_delete):
        """
        待删除本地化多语言数据语言的List
        :param language_list_to_delete:
        :return:
        """
        self._language_list_to_delete = language_list_to_delete
