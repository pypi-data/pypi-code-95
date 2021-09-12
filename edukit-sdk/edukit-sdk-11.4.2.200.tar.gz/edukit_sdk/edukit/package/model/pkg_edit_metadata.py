#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class PkgEditMetaData:
    def __init__(self):
        self._name = None
        self._default_lang = None
        self._remarks = None
        self._eduapp_purchased = None
        self._resident_league_app = None
        self._package_name = None
        self._source_name = None
        self._dist_notify_url = None
        self._refund_notify_url = None

    @property
    def default_lang(self):
        """
        :return:mixed
        """
        return self._default_lang

    @default_lang.setter
    def default_lang(self, default_lang):
        """
        缺省语言
        :param default_lang:
        :return:
        """
        self._default_lang = default_lang

    @property
    def remarks(self):
        """
        :return:mixed
        """
        return self._remarks

    @remarks.setter
    def remarks(self, remarks):
        """
        提供给审核/运营人员查看的备注信息，不对最终用户呈现
        :param remarks:
        :return:
        """
        self._remarks = remarks

    @property
    def eduapp_purchased(self):
        """
        :return:mixed
        """
        return self._eduapp_purchased

    @eduapp_purchased.setter
    def eduapp_purchased(self, eduapp_purchased):
        """
        本课程是否教育中心App直购
        :param eduapp_purchased:
        :return:
        """
        self._eduapp_purchased = eduapp_purchased

    @property
    def resident_league_app(self):
        """
        :return:mixed
        """
        return self._resident_league_app

    @resident_league_app.setter
    def resident_league_app(self, resident_league_app):
        """
        该内容所属应用AppId。需要注意：
        该应用在应用市场必须存在，且必须处于上架状态
        请求时，对于门户Portal，填写应用市场AppId(类似于c100123456);
        响应时，该字段只会填应用市场AppID。
        :param resident_league_app:
        :return:
        """
        self._resident_league_app = resident_league_app

    @property
    def package_name(self):
        """
        :return:mixed
        """
        return self._package_name

    @package_name.setter
    def package_name(self, package_name):
        """
        该内容所属应用包名，最大128，数据表字段预留；
        :param package_name:
        :return:
        """
        self._package_name = package_name

    @property
    def source_name(self):
        """
        :return:mixed
        """
        return self._source_name

    @source_name.setter
    def source_name(self, source_name):
        """
        appid为空时填写的来源信息
        :param source_name:
        :return:
        """
        self._source_name = source_name

    @property
    def dist_notify_url(self):
        """
        :return:mixed
        """
        return self._dist_notify_url

    @dist_notify_url.setter
    def dist_notify_url(self, dist_notify_url):
        """
        * CP发货商品，购买成功后的通知发货地址，由开发者指定；
        eduappPurchased = true时填写;
        :param dist_notify_url:
        :return:
        """
        self._dist_notify_url = dist_notify_url

    @property
    def name(self):
        """
        :return:mixed
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        缺省语言名称
        :param name:
        :return:
        """
        self._name = name

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
