# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.model.image_file_info import ImageFileInfo


class CourseLocalizedData:
    def __init__(self):
        self._name = None
        self._short_description = None
        self._deeplink_url = None
        self._cover_image_file_info = None
        self._portrait_cover_image_file_info = None
        self._introduce_image_file_infos = None
        self._full_description = None

    @property
    def name(self):
        """
        :return: mixed
        """
        return self._name

    @name.setter
    def name(self, name):
        """
         * 课程名称，说明如下：
         * 最大30字符（1个汉字也算1个字符）
         * 对于每种已添加的语言类型，课程提交前必须指定此字段。后续更新时可不携带此字段，此时将保留当前值不变
        :param name:
        :return:
        """
        self._name = name

    @property
    def short_description(self):
        """
        :return: mixed
        """
        return self._short_description

    @short_description.setter
    def short_description(self, short_description):
        """
         * 课程简要介绍，说明如下：
         * 最大40字符（1个汉字也算1个字符）
         * 对于每种已添加的语言类型，课程提交前必须指定此字段。后续更新时可不携带此字段，此时将保留当前值不变
        :param short_description:
        :return:
        """
        self._short_description = short_description

    @property
    def deeplink_url(self):
        """
        :return: mixed
        """
        return self._deeplink_url

    @deeplink_url.setter
    def deeplink_url(self, deeplink_url):
        """
         * 从教育中心App跳转到您的App的DeepLink链接，说明如下：
         * 如果用户需要跳转到您的App购买(eduappPurchased=false)或者学习
         (eduappUsed=false)此课程，在课程首次提交前必须提供此链接。
         如课程支持在教育中心直购和学习，则此字段为可选
         * 课程版本更新时可不携带此字段，此时将保留当前值不变
         * 从教育中心App通过此链接跳转到您的App后，您需要根据用户当前是否已购买此课程，确定展示购买页面还是学习页面
         * 可以在此链接中增加必要的参数以辅助跳转后在您的App内的逻辑处理，教育中心将透传这些参数。但请勿在链接中携带敏感数据（如用户密码等）
         * 提供此字段时，需要同时提供residentAGApp字段，以便能正确拉起您的App
        :param deeplink_url:
        :return:
        """
        self._deeplink_url = deeplink_url

    @property
    def cover_image_file_info(self):
        """
        :return: mixed
        """
        return self._cover_image_file_info

    @cover_image_file_info.setter
    def cover_image_file_info(self, cover_image_file_info: ImageFileInfo):
        # 横版封面图片文件信息
        self._cover_image_file_info = cover_image_file_info

    @property
    def portrait_cover_image_file_info(self):
        """
        :return: mixed
        """
        return self._portrait_cover_image_file_info

    @portrait_cover_image_file_info.setter
    def portrait_cover_image_file_info(
            self, portrait_cover_image_file_info: ImageFileInfo):
        """
        * 竖版封面图片文件信息
        * 课程类型为教辅教材时需要指定此字段
        :param portrait_cover_image_file_info:
        :return:
        """
        self._portrait_cover_image_file_info = portrait_cover_image_file_info

    @property
    def introduce_image_file_infos(self):
        """
        :return: mixed
        """
        return self._introduce_image_file_infos

    @introduce_image_file_infos.setter
    def introduce_image_file_infos(self,
                                   introduce_image_file_infos: ImageFileInfo):
        # 课程介绍图片文件信息列表
        self._introduce_image_file_infos = introduce_image_file_infos

    @property
    def full_description(self):
        """
        :return: mixed
        """
        return self._full_description

    @full_description.setter
    def full_description(self, full_description):
        """
         * 课程详细介绍，说明如下：
         * 最大2000字符（1个汉字也算1个字符）
         * 对于每种已添加的语言类型，课程提交前必须指定此字段。后续更新时可不携带此字段，此时将保留当前值不变
        :param full_description:
        :return:
        """
        self._full_description = full_description
