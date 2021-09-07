# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-09-01 13:52:58
@LastEditTime: 2021-09-01 14:23:30
@LastEditors: HuangJianYi
@Description: 
"""
from seven_framework import *
from seven_top import top


class PowerBaseModel():
    """
    :description:  商家权限处理
    """
    def get_config_data(self,store_user_nick,access_token):
        """
        :description: 获取项目编码
        :param num_iids：num_iids
        :param access_token：access_token
        :return 
        :last_editors: HuangJianYi
        """
        config_data = {}
        config_data["is_customized"] = 0
        shop_config_list = self.get_shop_config_list(store_user_nick)
        if len(shop_config_list) == 0:
            #获取项目编码
            project_code = self.get_project_code(store_user_nick, access_token)
            project_code_list = self.get_project_code_list(project_code)
            if len(project_code_list) > 0:
                config_data["function_config_list"] = project_code_list[0]["function_info_second_list"]
                config_data["skin_config_list"] = project_code_list[0]["skin_ids_second_list"]
        else:
            config_data["function_config_list"] = shop_config_list[0]["function_info_second_list"]
            config_data["skin_config_list"] = shop_config_list[0]["skin_ids_second_list"]
            config_data["is_customized"] = 1
        return config_data

    def get_project_code(self, store_user_nick, access_token):
        """
        :description: 获取项目编码
        :param store_user_nick：商家主账号昵称
        :param access_token：access_token
        :return 
        :last_editors: HuangJianYi
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.VasSubscribeGetRequest()

            req.article_code = config.get_value("article_code")
            req.nick = store_user_nick
            resp = req.getResponse(access_token)
            if "article_user_subscribe" not in resp["vas_subscribe_get_response"]["article_user_subscribes"].keys():
                return ""
            return resp["vas_subscribe_get_response"]["article_user_subscribes"]["article_user_subscribe"][0]["item_code"]
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            return ""

    def get_project_code_list(self, project_code):
        """
        :description:  获取公共功能列表
        :param project_code:收费项目代码（服务管理-收费项目列表）
        :return list: 
        :last_editors: WangQiang
        """

        project_code_list = []
        if not project_code:
            return project_code_list
        #产品id
        product_id = config.get_value("project_name")
        if not product_id:
            return project_code_list
        requst_url = "http://taobao-mp-s.gao7.com/general/project_code_list"
        data = {}
        data["project_code"] = project_code
        data["product_id"] = product_id
        result = HTTPHelper.get(requst_url, data, {"Content-Type": "application/json"})
        if result and result.ok and result.text:
            obj_data = self.json_loads(result.text)
            project_code_list = obj_data["Data"]
        return project_code_list

    def get_shop_config_list(self, store_user_nick):
        """
        :description:  获取店铺配置列表
        :param store_user_nick:商家主账号昵称
        :return list: 
        :last_editors: WangQiang
        """

        shop_config_list = []
        #产品id
        product_id = config.get_value("project_name")
        if not product_id:
            return shop_config_list
        requst_url = "http://taobao-mp-s.gao7.com/custom/query_skin_managemen_list"
        data = {}
        data["product_id"] = product_id
        data["store_user_nick"] = store_user_nick
        result = HTTPHelper.get(requst_url, data, {"Content-Type": "application/json"})
        if result and result.ok and result.text:
            obj_data = self.json_loads(result.text)
            shop_config_list = obj_data["Data"]
        return shop_config_list