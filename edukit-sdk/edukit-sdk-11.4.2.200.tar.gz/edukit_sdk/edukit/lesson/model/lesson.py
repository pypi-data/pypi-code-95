# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class Lesson:
    def __init__(self):
        self._lesson_id = None
        self._meta_data = None
        self._multi_lang_localized_data_list = None
        self._language_list_to_delete = None
        self._catalogue_id = None
        self._progress_callback = None

    @property
    def lesson_id(self):
        """
        :return:mixed
        """
        return self._lesson_id

    @lesson_id.setter
    def lesson_id(self, lesson_id):
        """
        设置章节ID。创建章节时由教育中心生成，用于唯一标识一个章节，调用getLessonId()获取。
        :param lesson_id:
        """
        self._lesson_id = lesson_id

    @property
    def meta_data(self):
        """
        :return:mixed
        """
        return self._meta_data

    @meta_data.setter
    def meta_data(self, meta_data):
        """
        设置章节元数据。
        :param meta_data:
        """
        self._meta_data = meta_data

    @property
    def multi_lang_localized_data_list(self):
        """
        :return:mixed
        """
        return self._multi_lang_localized_data_list

    @multi_lang_localized_data_list.setter
    def multi_lang_localized_data_list(self, multi_lang_localized_data_list):
        """
        设置章节本地化多语言数据列表。
        :param multi_lang_localized_data_list:
        """
        self._multi_lang_localized_data_list = multi_lang_localized_data_list

    @property
    def language_list_to_delete(self):
        """
        :return:mixed
        """
        return self._language_list_to_delete

    @language_list_to_delete.setter
    def language_list_to_delete(self, language_list_to_delete):
        """
        设置需要删除的多语言列表。
        整体删除指定语言的所有多语言数据。如仅需要删除或更新特定语言下的特定字段，可构造LessonMultiLanguageData对象。
        简体中文及默认语言的多语言数据不允许删除。
        语言代码由BCP-47定义，如简体中文为"zh-CN"，区分大小写（语言标识使用小写字母；区域名称使用大写字母）。
        :param language_list_to_delete :
        """
        self._language_list_to_delete = language_list_to_delete

    @property
    def progress_callback(self):
        """
        :return:mixed
        """
        return self._progress_callback

    @progress_callback.setter
    def progress_callback(self, progress_callback):
        """
        设置文件上传进度回调函数。
        :param progress_callback:
        """
        self._progress_callback = progress_callback

    @property
    def catalogue_id(self):
        """
        :return:mixed
        """
        return self._catalogue_id

    @catalogue_id.setter
    def catalogue_id(self, catalogue_id):
        """
        章节关联的目录ID
        :param catalogue_id:
        """
        self._catalogue_id = catalogue_id
