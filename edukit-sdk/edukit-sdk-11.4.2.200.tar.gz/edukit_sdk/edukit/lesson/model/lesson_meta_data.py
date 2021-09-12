# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class LessonMetaData:
    def __init__(self):
        self._name = None
        self._default_lang = None
        self._free_flag = None
        self._available_from = None
        self._available_before = None
        self._display_order = None
        self._edu_app_used = None
        self._media_type = None

    @property
    def default_lang(self):
        """
        :return:mixed
        """
        return self._default_lang

    @default_lang.setter
    def default_lang(self, default_lang):
        """
        设置默认语言。
        您可以提供多语言的章节信息，教育中心客户端向用户展示章节时，会优先匹配用户设备设置的系统语言。如您未提供用户系统语言对应的章节信息，将展示默认语言对应的数据。
        您必须提供默认语言对应的章节信息。
        章节首次提交审核前必须指定此字段；后续更新时如不指定此字段则保留当前值。
        当前华为教育中心仅在中国大陆地区提供服务，默认语言建议设置为简体中文(“zh-CN”)。
        语言代码由BCP-47定义，如简体中文为"zh-CN"，区分大小写（语言标识使用小写字母；区域名称使用大写字母）。
        :param default_lang:
        """
        self._default_lang = default_lang

    @property
    def free_flag(self):
        """
        :return:mixed
        """
        return self._free_flag

    @free_flag.setter
    def free_flag(self, free_flag):
        """
        设置是否免费章节标记。
        章节首次提交时，必须通过此字段指定是否为免费章节。后续更新时可不携带此字段，此时将保留当前值不变。
        只       有付费课程允许有付费章节；如果课程本身为免费，此字段将被忽略。
        true-免费
        false-付费
        如果选择付费章节，须确保开发者账号已完成商户认证，否则无法提交成功。
        :param free_flag:
        """
        self._free_flag = free_flag

    @property
    def available_from(self):
        """
        :return:mixed
        """
        return self._available_from

    @available_from.setter
    def available_from(self, available_from):
        """
        设置章节最早可用时间。
        该时间必须晚于当前时间。考虑到服务器时间可能存在差异，应尽量避免指定距离当前时间过近的时间。
        该字段当前主要用于直播类课程，指定直播开始时间。直播课程的章节必须携带；非直播类课程可不指定此时间。
        首次提交设置此时间后，后续更新时可不携带此字段，此时将保留当前值不变。
        直播课直        播时间过后将自动变为视频课，无需再更新此时间。
        时间格式使用RFC3339定义的UTC时间格式（即GMT+00时区的时间），例：2021-12-20T08:00:00Z。
        :param available_from:
        """
        self._available_from = available_from

    @property
    def available_before(self):
        """
        :return:mixed
        """
        return self._available_before

    @available_before.setter
    def available_before(self, available_before):
        """
        设置章节最晚可用时间。
        该时间必须必须晚于课程最早可用时间（availableFrom字段）。
        该字      段当前主要用于直播类课程，指定直播结束时间。直播课程的章节必须携带；非直播类课程可不指定此时间。
        首次提交设置此时间后，后续更新时可不携带此字段，此时将保留当前值不变。
        直播课直播时间过后将自动变为视频课，无需再更新此时间。
        :param available_before:
        """
        self._available_before = available_before

    @property
    def display_order(self):
        """
        :return:mixed
        """
        return self._display_order

    @display_order.setter
    def display_order(self, display_order):
        """
        设置章节序号。
        同一课程        章节列表中该章节的排列顺序，例如：1表示当前章节排在所属课程章节列表的第一个。
        该序号用于控制章节在课程目录列表中的展示顺序；序号越小展示越靠前。
        如未指定该字段，创建课程时将从100开始取当前章节序号最大值+1作为新建章节的序号；更新章节时当前序号不变（更新章节版本元数据时可以修改）。
        该序号不直接向用户展示，只作为排序依据。因此建议章节序号之间保留一定的间隙，以应对需要在两个章节之间插入新章节的场景。
        取值范围：0~9999。
        :param display_order:
        """
        self._display_order = display_order

    @property
    def edu_app_used(self):
        """
        :return:mixed
        """
        return self._edu_app_used

    @edu_app_used.setter
    def edu_app_used(self, edu_app_used):
        """
        设置章节是否支持在教育中心中学习标记。
        对       于视频/音频类课程，将音视频文件上传到教育中心后，可以设置为true，支持在教育中心学习，由教育中心客户端直接播放。
        如设置为false，用户在教育中心学习该章节时，将通过DeepLink拉起课程元数据中residentAGApp字段对应的应用。
        章节首次提交审核前必须指定此字段；课程审核通过上架后，此字段将不能再修改。
        同一课程的不同章节，可以设置不同的属性值。
        :param edu_app_used:
        """
        self._edu_app_used = edu_app_used

    @property
    def media_type(self):
        """
        :return:mixed
        """
        return self._media_type

    @media_type.setter
    def media_type(self, media_type):
        """
        设置章节媒体类型。
        如果课程类型为绘本，该字段必填。
        支持的取值如下：
        1：音频
        2：视频
        3：绘本
        :param media_type:
        """
        self._media_type = media_type

    @property
    def name(self):
        """
        :return:mixed
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        设置默认语言对应的章节名称。
        需要与章节多语言数据中defaultLang对应语言的名称相同。
        章节首次提交前必须指定此字段；后续更新时如不指定此字段则保留当前值。
        :param name:
        """
        self._name = name
