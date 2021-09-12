# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class CourseEditMetaData:
    def __init__(self):
        self._validity_num = None
        self._default_lang = None
        self._category_ids = None
        self._tag_ids = None
        self._resident_a_g_app = None
        self._source_name = None
        self._selling_mode = None
        self._remarks = None
        self._available_from = None
        self._available_before = None
        self._name = None
        self._auto_status_change = None
        self._eduapp_used = None
        self._eduapp_purchased = None
        self._dev_product_id = None
        self._dist_notify_url = None
        self._validity_unit = None
        self._include_lessons = None
        self._type_id = None
        self._teachers = None
        self._need_delivery = None
        self._media_type = None
        self._refund_notify_url = None

    @property
    def auto_status_change(self):
        """
        :return: mixed
        """
        return self._auto_status_change

    @auto_status_change.setter
    def auto_status_change(self, auto_status_change):
        """
        自动状态变更设置
        :param auto_status_change:
        :return:
        """
        self._auto_status_change = auto_status_change

    @property
    def default_lang(self):
        """
        :return: mixed
        """
        return self._default_lang

    @default_lang.setter
    def default_lang(self, default_lang):
        """
        课程的默认语言代码
        :param default_lang:
        :return:
        """
        self._default_lang = default_lang

    @property
    def available_before(self):
        """
        :return: mixed
        """
        return self._available_before

    @available_before.setter
    def available_before(self, available_before):
        """
        课程最晚可用时间
        :param available_before:
        :return:
        """
        self._available_before = available_before

    @property
    def available_from(self):
        """
        :return: mixed
        """
        return self._available_from

    @available_from.setter
    def available_from(self, available_from):
        """
        课程最早可用时间
        :param available_from:
        :return:
        """
        self._available_from = available_from

    @property
    def category_ids(self):
        """
        :return: mixed
        """
        return self._category_ids

    @category_ids.setter
    def category_ids(self, category_ids):
        """
        课程三级分类ID列表，请参见课程分类ID
        :param category_ids:
        :return:
        """
        self._category_ids = category_ids

    @property
    def dist_notify_url(self):
        """
        :return: mixed
        """
        return self._dist_notify_url

    @dist_notify_url.setter
    def dist_notify_url(self, dist_notify_url):
        """
        用户直购课程的发货通知地址(HTTPS URL)
        :param dist_notify_url:
        :return:
        """
        self._dist_notify_url = dist_notify_url

    @property
    def eduapp_purchased(self):
        """
        :return: mixed
        """
        return self._eduapp_purchased

    @eduapp_purchased.setter
    def eduapp_purchased(self, eduapp_purchased):
        """
        课程是否支持直接在教育中心App购买
        :param eduapp_purchased:
        :return:
        """
        self._eduapp_purchased = eduapp_purchased

    @property
    def eduapp_used(self):
        """
        :return: mixed
        """
        return self._eduapp_used

    @eduapp_used.setter
    def eduapp_used(self, eduapp_used):
        """
        课程是否支持在教育中心学习
        :param eduapp_used:
        :return:
        """
        self._eduapp_used = eduapp_used

    @property
    def include_lessons(self):
        """
        :return: mixed
        """
        return self._include_lessons

    @include_lessons.setter
    def include_lessons(self, include_lessons):
        """
        本课程是否包含章节
        :param include_lessons:
        :return:
        """
        self._include_lessons = include_lessons

    @property
    def name(self):
        """
        :return: mixed
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        默认语言（见defaultLang字段说明）对应的课程名称
        :param name:
        :return:
        """
        self._name = name

    @property
    def remarks(self):
        """
        :return: mixed
        """
        return self._remarks

    @remarks.setter
    def remarks(self, remarks):
        """
        提供给审核/运营人员查看的备注信息
        :param remarks:
        :return:
        """
        self._remarks = remarks

    @property
    def resident_a_g_app(self):
        """
        :return: mixed
        """
        return self._resident_a_g_app

    @resident_a_g_app.setter
    def resident_a_g_app(self, resident_a_g_app):
        """
        该课程所属应用在华为应用市场的AppID
        :param resident_a_g_app:
        :return:
        """
        self._resident_a_g_app = resident_a_g_app

    @property
    def selling_mode(self):
        """
        :return: mixed
        """
        return self._selling_mode

    @selling_mode.setter
    def selling_mode(self, selling_mode):
        """
        课程售卖模式，说明如下：
        支持如下取值：
        0：单课程售卖
        1：免费
        2：仅支持会员包售卖
        3：同时支持单课程售卖和会员包售卖
        :param selling_mode:
        :return:
        """
        self._selling_mode = selling_mode

    @property
    def source_name(self):
        """
        :return: mixed
        """
        return self._source_name

    @source_name.setter
    def source_name(self, source_name):
        """
        课程来源名称
        :param source_name:
        :return:
        """
        self._source_name = source_name

    @property
    def tag_ids(self):
        """
        :return: mixed
        """
        return self._tag_ids

    @tag_ids.setter
    def tag_ids(self, tag_ids):
        """
        课程标签列表，请参见课程标签ID
        :param tag_ids:
        :return:
        """
        self._tag_ids = tag_ids

    @property
    def teachers(self):
        """
        :return: mixed
        """
        return self._teachers

    @teachers.setter
    def teachers(self, teachers):
        """
        课程教师ID列表
        :param teachers:
        :return:
        """
        self._teachers = teachers

    @property
    def type_id(self):
        """
        :return: mixed
        """
        return self._type_id

    @type_id.setter
    def type_id(self, type_id):
        """
        课程类型
        :param type_id:
        :return:
        """
        self._type_id = type_id

    @property
    def validity_num(self):
        """
        :return: mixed
        """
        return self._validity_num

    @validity_num.setter
    def validity_num(self, validity_num):
        """
        课程订购关系有效期长度
        :param validity_num:
        :return:
        """
        self._validity_num = validity_num

    @property
    def validity_unit(self):
        """
        :return: mixed
        """
        return self._validity_unit

    @validity_unit.setter
    def validity_unit(self, validity_unit):
        """
        课程订购关系有效期长度单位
        :param validity_unit:
        :return:
        """
        self._validity_unit = validity_unit

    @property
    def media_type(self):
        """
        :return: mixed
        """
        return self._media_type

    @media_type.setter
    def media_type(self, media_type):
        """
        课程媒体类型：1：音频 2：视频 3：绘本
        :param media_type:
        :return:
        """
        self._media_type = media_type

    @property
    def need_delivery(self):
        """
        :return: mixed
        """
        return self._need_delivery

    @need_delivery.setter
    def need_delivery(self, need_delivery):
        """
        课程购买后是否需要邮寄材料
        :param need_delivery:
        :return:
        """
        self._need_delivery = need_delivery

    @property
    def dev_product_id(self):
        """
        :return: mixed
        """
        return self._dev_product_id

    @dev_product_id.setter
    def dev_product_id(self, dev_product_id):
        """
        课程关联商品ID
        :param dev_product_id:
        :return:
        """
        self._dev_product_id = dev_product_id

    @property
    def refund_notify_url(self):
        """
        :return: mixed
        """
        return self._refund_notify_url

    @refund_notify_url.setter
    def refund_notify_url(self, refund_notify_url):
        """
        退款通知地址
        :param refund_notify_url:
        :return:
        """
        self._refund_notify_url = refund_notify_url
