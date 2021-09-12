#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
from edukit_sdk.edukit.common.model.image_file_info import ImageFileInfo


class TeacherLocalizedData:
    def __init__(self):
        self._language = None
        self._name = None
        self._description = None
        self._teacher_portrait = None
        self._portrait_id = None

    @property
    def name(self):
        """
        :return: mixed
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        教师姓名
        最大30字符（1个汉字也算1个字符）
        对于每种已添加的语言类型，提交教师信息前必须指定此字段。后续更新时可不携带此字段，此时将保留当前值不变
        :param name:
        :return:
        """
        self._name = name

    @property
    def description(self):
        """
        :return: mixed
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        教师介绍
        最大500字符（1个汉字也算1个字符）
        对于每种已添加的语言类型，提交教师信息前必须指定此字段。后续更新时可不携带此字段，此时将保留当前值不变
        :param description:
        :return:
        """
        self._description = description

    @property
    def teacher_portrait(self):
        """
        :return: mixed
        """
        return self._teacher_portrait

    @teacher_portrait.setter
    def teacher_portrait(self, teacher_portrait: ImageFileInfo):
        """
        上传文件信息 详见ImageFileInfo类
        :param teacher_portrait:
        :return:
        """
        self._teacher_portrait = teacher_portrait

    @property
    def portrait_id(self):
        """
        :return: mixed
        """
        return self._portrait_id

    @portrait_id.setter
    def portrait_id(self, portrait_id):
        self._portrait_id = portrait_id

    @property
    def language(self):
        """
        :return: mixed
        """
        return self._language

    @language.setter
    def language(self, language):
        """
        教师语言信息
        语言代码由BCP-47定义，如简体中文为"zh-CN"，区分大小写（语言标识使用小写字母；区域名称使用大写字母）
        :param language:
        :return:
        """
        self._language = language