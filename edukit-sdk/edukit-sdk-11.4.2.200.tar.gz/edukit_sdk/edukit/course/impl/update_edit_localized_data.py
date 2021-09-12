# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class UpdateEditLocalizedData:
    def __init__(self):
        self._name = None  # 课程名称
        self._short_description = None  # 课程简要介绍
        self._full_description = None  # 课程详细介绍
        self._cover_id = None  # 横版封面图片的文件的素材id
        self._portrait_cover_id = None  # 竖版封面图片的文件的素材id
        self._introduce_ids = None  # 课程介绍图片文件的素材id列表
        self._deeplink_url = None  # 从教育中心App跳转到您的App的DeepLink链接

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def cover_id(self):
        return self._cover_id

    @cover_id.setter
    def cover_id(self, cover_id):
        self._cover_id = cover_id

    @property
    def short_description(self):
        return self._short_description

    @short_description.setter
    def short_description(self, short_description):
        self._short_description = short_description

    @property
    def portrait_cover_id(self):
        return self._portrait_cover_id

    @portrait_cover_id.setter
    def portrait_cover_id(self, portrait_cover_id):
        self._portrait_cover_id = portrait_cover_id

    @property
    def introduce_ids(self):
        return self._introduce_ids

    @introduce_ids.setter
    def introduce_ids(self, introduce_ids):
        self._introduce_ids = introduce_ids

    @property
    def deeplink_url(self):
        return self._deeplink_url

    @deeplink_url.setter
    def deeplink_url(self, deeplink_url):
        self._deeplink_url = deeplink_url

    @property
    def full_description(self):
        return self._full_description

    @full_description.setter
    def full_description(self, full_description):
        self._full_description = full_description

