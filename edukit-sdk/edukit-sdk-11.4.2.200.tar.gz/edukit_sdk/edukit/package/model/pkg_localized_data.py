#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class PkgLocalizedData:
    def __init__(self):
        self._language = None
        self._name = None
        self._cover_image_info = None
        self._full_description = None
        self._introduce_infos = None
        self._cover_image_id = None
        self._introduce_ids = None

    @property
    def language(self):
        """
        :return:mixed
        """
        return self._language

    @language.setter
    def language(self, language):
        """
        语言代码由[BCP-47]定义，如简体中文为"zh-CN"，区分大小写（语言标识使用小写字母；区域名称使用大写字母
        :param language:
        :return:
        """
        self._language = language

    @property
    def cover_image_info(self):
        """
        :return: mixed
        """
        return self._cover_image_info

    @cover_image_info.setter
    def cover_image_info(self, cover_image_info):
        """
        会员包封面图片
        :param cover_image_info:
        :return:
        """
        self._cover_image_info = cover_image_info

    @property
    def name(self):
        """
        :return:mixed
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        会员包名称
        :param name:
        :return:
        """
        self._name = name

    @property
    def introduce_infos(self):
        """
        :return:mixed
        """
        return self._introduce_infos

    @introduce_infos.setter
    def introduce_infos(self, introduce_infos):
        """
        介绍图片素材Id列表，更新时必须全量提交
        :param introduce_infos:
        :return:
        """
        self._introduce_infos = introduce_infos

    @property
    def cover_image_id(self):
        """
        :return:mixed
        """
        return self._cover_image_id

    @cover_image_id.setter
    def cover_image_id(self, cover_image_id):
        """
        会员包封面图片文件的素材ID
        :param cover_image_id:
        :return:
        """
        self._cover_image_id = cover_image_id

    @property
    def full_description(self):
        """
        :return:mixed
        """
        return self._full_description

    @full_description.setter
    def full_description(self, full_description):
        """
        会员包详细介绍。最大2000字符
        :param full_description:
        :return:
        """
        self._full_description = full_description

    @property
    def introduce_ids(self):
        """
        :return:mixed
        """
        return self._introduce_ids

    @introduce_ids.setter
    def introduce_ids(self, introduce_ids):
        """
        会员包介绍图片文件的素材ID列表
        :param introduce_ids:
        :return:
        """
        self._introduce_ids = introduce_ids
