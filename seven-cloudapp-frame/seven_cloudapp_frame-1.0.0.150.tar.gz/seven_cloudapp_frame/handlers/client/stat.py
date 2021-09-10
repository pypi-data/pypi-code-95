# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-09-10 11:29:31
@LastEditTime: 2021-09-10 11:39:09
@LastEditors: HuangJianYi
@Description: 处理数据统计上报
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.stat_base_model import *


class ShareReportHandler(TaoBaseHandler):
    """
    :description: 处理分享上报
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理分享上报
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        stat_base_model = StatBaseModel(context=self)

        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token, self.request_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        is_stat = invoke_result_data.data["is_stat"] if invoke_result_data.data.__contains__("is_stat") else True
        invoke_result_data = stat_base_model.process_share_report(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, check_user_nick, continue_request_expire, is_stat)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(invoke_result_data, app_id, act_id, user_id, module_id, login_token, self.request_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)

    def business_process_executing(self, app_id, act_id, user_id, module_id, login_token, request_params):
        """
        :description: 执行前事件
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param login_token:访问令牌
        :param request_params: 请求参数字典
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data.data = {"check_user_nick": True, "continue_request_expire": 5}
        return invoke_result_data

    def business_process_executed(self, invoke_result_data, app_id, act_id, user_id, module_id, login_token, request_params):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param login_token:访问令牌
        :param request_params: 请求参数字典
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data


class InviteReportHandler(TaoBaseHandler):
    """
    :description: 处理邀请进入上报
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 处理分享上报
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        module_id = int(self.get_param("module_id", 0))
        login_token = self.get_param("login_token")
        stat_base_model = StatBaseModel(context=self)

        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token, self.request_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        check_user_nick = invoke_result_data.data["check_user_nick"] if invoke_result_data.data.__contains__("check_user_nick") else True
        continue_request_expire = invoke_result_data.data["continue_request_expire"] if invoke_result_data.data.__contains__("continue_request_expire") else 5
        is_stat = invoke_result_data.data["is_stat"] if invoke_result_data.data.__contains__("is_stat") else True
        invoke_result_data = stat_base_model.process_invite_report(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, check_user_nick, continue_request_expire, is_stat)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(invoke_result_data, app_id, act_id, user_id, module_id, login_token, self.request_params)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)

    def business_process_executing(self, app_id, act_id, user_id, module_id, login_token, request_params):
        """
        :description: 执行前事件
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param login_token:访问令牌
        :param request_params: 请求参数字典
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data.data = {"check_user_nick": True, "continue_request_expire": 5}
        return invoke_result_data

    def business_process_executed(self, invoke_result_data, app_id, act_id, user_id, module_id, login_token, request_params):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param login_token:访问令牌
        :param request_params: 请求参数字典
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data