# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-06-02 11:08:39
:LastEditTime: 2021-04-15 14:59:41
:LastEditors: HuangJingCan
:description: App相关
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.handlers.server.app_s import TelephoneHandler
from seven_cloudapp.handlers.server.app_s import AppUpdateHandler
from seven_cloudapp.handlers.server.app_s import AppInfoHandler

from seven_cloudapp.models.db_models.base.base_info_model import *


class BaseInfoHandler(SevenBaseHandler):
    """
    :description: 基础信息处理
    """
    def get_async(self):
        """
        :description: 基础信息获取
        :param 
        :return: dict
        :last_editors: HuangJianYi
        """
        base_info = BaseInfoModel(context=self).get_entity()
        if not base_info:
            return self.reponse_json_error("BaseInfoError", "基础信息出错")

        # 左上角信息
        info = {}
        info["company"] = "天志互联"
        info["miniappName"] = base_info.product_name
        info["logo"] = base_info.product_icon

        # 左边菜单
        menu_list = []
        menu = {}
        menu["name"] = "创建活动"
        menu["key"] = "create_action"
        menu_list.append(menu)
        menu = {}
        menu["name"] = "活动管理"
        menu["key"] = "act_manage"
        menu_list.append(menu)
        menu = {}
        menu["name"] = "装修教程"
        menu["key"] = "decoration_poster"
        menu_list.append(menu)
        menu = {}
        menu["name"] = "版本更新"
        menu["key"] = "update_ver"
        menu_list.append(menu)

        # 左边底部菜单
        bottom_button_list = []
        bottom_button = {}
        bottom_button["title"] = "发票管理"
        bottom_button["handling_event"] = "popup"
        bottom_button["event_name"] = "billManage"
        bottom_button_list.append(bottom_button)
        bottom_button = {}
        bottom_button["title"] = "配置教程"
        bottom_button["handling_event"] = "popup"
        bottom_button["event_name"] = "use_teaching"
        bottom_button_list.append(bottom_button)
        bottom_button = {}
        bottom_button["title"] = "联系旺旺"
        bottom_button["handling_event"] = "outtarget"
        bottom_button["event_name"] = "http://amos.alicdn.com/getcid.aw?v=2&uid=%E5%A4%A9%E5%BF%97%E4%BA%92%E8%81%94&site=cntaobao&s=1&groupid=0&charset=utf-8"
        bottom_button_list.append(bottom_button)
        bottom_button = {}
        bottom_button["title"] = "号码绑定"
        bottom_button["handling_event"] = "popup"
        bottom_button["event_name"] = "bind_phone"
        bottom_button_list.append(bottom_button)

        # 右边使用指引
        use_point_list = []
        use_point = {}
        use_point["index"] = "1"
        use_point["title"] = "创建活动并配置完成"
        use_point_list.append(use_point)
        use_point = {}
        use_point["index"] = "2"
        use_point["title"] = "将淘宝小程序装修至店铺"
        use_point_list.append(use_point)
        use_point = {}
        use_point["index"] = "3"
        use_point["title"] = "正式运营淘宝小程序"
        use_point_list.append(use_point)

        default_box_style = {}
        default_box_style["title"] = "默认模板"
        default_box_style["pic_url"] = "https://isv.alibabausercontent.com/00000000/imgextra/i3/2206353354303/O1CN016E9TQD1heotGpXFkW_!!2206353354303-2-isvtu-00000000.png"

        data = {}
        data["serverName"] = "在线拆盲盒模板"
        data["info"] = info
        data["menu"] = menu_list
        data["bottom_button"] = bottom_button_list
        data["use_point"] = use_point_list
        data["default_box_style"] = default_box_style
        if base_info:
            # 把string转成数组对象
            base_info.update_function = self.json_loads(base_info.update_function) if base_info.update_function else []
            base_info.price_gare = self.json_loads(base_info.price_gare) if base_info.price_gare else []
            base_info.product_price = self.json_loads(base_info.product_price) if base_info.product_price else []
            base_info.decoration_poster = self.json_loads(base_info.decoration_poster) if base_info.decoration_poster else []
            base_info.friend_link = self.json_loads(base_info.friend_link) if base_info.friend_link else []
            base_info.menu_config = self.json_loads(base_info.menu_config) if base_info.menu_config else []
            #指定账号升级
            user_nick = self.get_taobao_param().user_nick
            if user_nick:
                if user_nick == config.get_value("test_user_nick"):
                    base_info.client_ver = config.get_value("test_client_ver")
                    base_info.update_function = []
            data["base_info"] = base_info.__dict__

        if base_info:
            return self.reponse_json_success(data)

        return self.reponse_json_error("BaseInfoError", "基础信息出错")