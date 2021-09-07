# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-04-14 15:02:54
@LastEditTime: 2021-09-01 14:40:00
@LastEditors: HuangJianYi
:Description: 用户权限相关
"""
from seven_cloudapp.handlers.seven_base import *
from seven_cloudapp_ppmt.models.power_base_model import *


class GetPowerMenuHandler(SevenBaseHandler):
    """
    :description: 获取权限菜单列表
    """
    def get_async(self):
        """
        :description: 获取权限菜单列表
        :return: dict
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id

        data = self.get_power_menu(app_id)

        return self.reponse_json_success(data)


class ShopPowerConfigHandler(SevenBaseHandler):
    """
    :description: 商家权限配置处理
    """
    def get_async(self):
        """
        :description: 获取商家权限配置
        :return: reponse_json_success
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if not app_info:
            return self.reponse_json_error("NoApp", "对不起，找不到该小程序")
        power_base_model = PowerBaseModel()
        self.reponse_json_success(power_base_model.get_config_data(app_info.store_user_nick, self.get_taobao_param().access_token))
