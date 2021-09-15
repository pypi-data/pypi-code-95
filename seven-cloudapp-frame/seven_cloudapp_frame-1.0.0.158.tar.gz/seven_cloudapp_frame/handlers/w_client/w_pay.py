# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-09-13 16:49:46
@LastEditTime: 2021-09-15 14:24:14
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.libs.customize.seven_helper import SevenHelper
from seven_cloudapp_frame.libs.customize.wechat_helper import WeChatPayRequest, WeChatPayReponse, WeChatRefundReponse
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.db_models.pay.pay_order_model import *
from seven_cloudapp_frame.models.db_models.refund.refund_order_model import *


class VoucherOrderHandler(ClientBaseHandler):
    """
    :description: 创建微信预订单
    """
    @filter_check_params("user_id,pay_order_no")
    @filter_check_head_sign()
    @filter_check_params_sign()
    def get_async(self):
        """
        :description: 创建微信预订单
        :param pay_order_no:支付单号
        :param user_id:用户标识
        :return: 请求接口获取客户端需要的支付密钥数据
        :last_editors: HuangJianYi
        """
        user_id = int(self.get_param("user_id", 0))
        pay_order_no = self.get_param("pay_order_no")
        invoke_result_data = InvokeResultData()

        if SevenHelper.is_continue_request(f"VoucherOrder_{str(user_id)}") == True:
            return self.response_json_error("error", "对不起,请求太频繁")
        pay_order_model = PayOrderModel(context=self)
        pay_order = pay_order_model.get_entity("pay_order_no=%s", params=[pay_order_no])
        if not pay_order or pay_order.order_status != 0:
            return self.response_json_error("error", "抱歉!未查询到订单信息,请联系客服")
        pay_config = config.get_value("wechat_pay")
        pay_notify_url = pay_config["pay_notify_url"]

        # 商品说明
        body = pay_order.order_name
        # 金额
        total_fee = pay_order.pay_amount
        # ip
        ip = SevenHelper.get_first_ip()

        try:
            invoke_result_data = self.business_process_executing(self.request_params)
            if invoke_result_data.success == True:
                pay_notify_url = invoke_result_data.data["pay_notify_url"] if invoke_result_data.data.__contains__("pay_notify_url") else pay_notify_url
                time_expire = invoke_result_data.data["time_expire"] if invoke_result_data.data.__contains__("time_expire") else str(SevenHelper.get_now_int(1))  #交易结束时间,设置1小时
            invoke_result_data = WeChatPayRequest().create_order(pay_order_no, body, total_fee, ip, pay_notify_url, pay_order.open_id, time_expire)
            if invoke_result_data.success == False:
                return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)

            # self.logging_link_info('小程序支付返回前端参数:' + str(invoke_result_data.data))
            invoke_result_data = self.business_process_executed(invoke_result_data, self.request_params)
            return self.response_json_success(invoke_result_data.data)
        except Exception as ex:
            self.logging_link_error("【创建微信预订单异常】" + str(ex))
            return self.response_json_error("fail", "请重新支付")

    def business_process_executing(self, request_params):
        """
        :description: 执行前事件
        :param request_params: 请求参数字典
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data.data = {}
        return invoke_result_data

    def business_process_executed(self, invoke_result_data, request_params):
        """
        :description: 执行后事件
        :param invoke_result_data: invoke_result_data
        :param request_params: 请求参数字典
        :return:
        :last_editors: HuangJianYi
        """
        return invoke_result_data


class PayNotifyHandler(ClientBaseHandler):
    """
    :description: 微信支付异步通知
    """
    @filter_check_params()
    def post_async(self):
        """
        :description:支付异步通知
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        xml_params = self.request.body.decode('utf-8')
        wechat_pay_reponse = None
        try:
            wechat_pay_reponse = WeChatPayReponse(xml_params)  # 创建对象
            response_result = wechat_pay_reponse.get_data()
            return_code = response_result["return_code"]
            result_code = response_result["result_code"]
            if return_code == "FAIL":
                return self.write(wechat_pay_reponse.response_xml(response_result["return_msg"], False))
            if result_code == "FAIL":
                return self.write(wechat_pay_reponse.response_xml(response_result["err_code_des"], False))
            if wechat_pay_reponse.check_sign() != True:  # 校验签名,成功则继续后续操作
                return self.write(wechat_pay_reponse.response_xml("签名验证失败", False))
            total_fee = response_result["total_fee"]
            pay_order_no = response_result["out_trade_no"]

            pay_order_model = PayOrderModel(context=self)
            pay_order = pay_order_model.get_entity("pay_order_no=%s", params=[pay_order_no])
            if not pay_order:
                return self.write(wechat_pay_reponse.response_xml("未查询到订单信息", False))
            # 判断金额是否匹配
            if int(decimal.Decimal(str(pay_order.pay_amount)) * 100) != int(total_fee):
                self.logging_link_error(f"微信支付订单[{pay_order_no}] 金额不匹配疑似刷单.数据库金额:{str(pay_order.pay_amount)} 平台回调金额:{str(total_fee)}")
                return self.write(wechat_pay_reponse.response_xml("金额异常", False))

            invoke_result_data = self.business_process_executing(self.request_params)
            if invoke_result_data.success == False:
                return self.write(wechat_pay_reponse.response_xml(invoke_result_data.error_message, False))
            self.business_process_executed(pay_order,response_result)

            return self.write(wechat_pay_reponse.response_xml("SUCCESS", True))

        except Exception as ex:
            self.logging_link_error(str(ex) + "【微信支付异步通知】" + str(xml_params))
            return self.write(wechat_pay_reponse.response_xml("数据异常", False))

    def business_process_executing(self, request_params):
        """
        :description: 执行前事件
        :param request_params: 请求参数字典
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        return invoke_result_data

    def business_process_executed(self, pay_order, response_result):
        """
        :description: 执行后事件
        :param pay_order: 支付订单实体模型
        :param response_result: 响应参数字典
        :return:
        :last_editors: HuangJianYi
        """
        pay_order_model = PayOrderModel(context=self)
        transaction_id = response_result["transaction_id"]
        time_string = response_result["time_end"]
        if pay_order.order_status == 0 or pay_order.order_status == 2:
            pay_order.out_order_no = transaction_id
            pay_order.order_status = 1
            pay_order.pay_date = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(time_string, "%Y%m%d%H%M%S"))
            pay_order_model.update_entity(pay_order, "out_order_no,order_status,pay_date")


class RefundNotifyHandler(ClientBaseHandler):
    """
    :description: 微信退款异步通知
    """
    @filter_check_params()
    def post_async(self):
        invoke_result_data = InvokeResultData()
        xml_params = self.request.body.decode('utf-8')
        wechat_refund_reponse = None
        try:
            wechat_refund_reponse = WeChatRefundReponse(xml_params)  # 创建对象
            response_result = wechat_refund_reponse.get_data()
            return_code = response_result["return_code"]
            result_code = response_result["result_code"]
            if return_code == "FAIL":
                return self.write(wechat_refund_reponse.response_xml(response_result["return_msg"], False))
            if result_code == "FAIL":
                return self.write(wechat_refund_reponse.response_xml(response_result["err_code_des"], False))
            invoke_result_data = self.business_process_executing(self.request_params)
            if invoke_result_data.success == False:
                return self.write(wechat_refund_reponse.response_xml(invoke_result_data.error_message, False))
            # 解密
            req_info_dict = wechat_refund_reponse.decode_req_info(response_result["req_info"])
            req_info_dict = req_info_dict["root"]
            self.business_process_executed(req_info_dict,self.request_params)
            return self.write(wechat_refund_reponse.response_xml("SUCCESS", True))
        except Exception as ex:
            self.logging_link_error(str(ex) + "【微信退款异步通知】" + str(xml_params))
            return self.write(wechat_refund_reponse.response_xml("数据异常", False))

    def business_process_executing(self, request_params):
        """
        :description: 执行前事件
        :param request_params: 请求参数字典
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        return invoke_result_data

    def business_process_executed(self, req_info_dict, request_params):
        """
        :description: 执行后事件
        :param req_info_dict: 退款解密信息
        :param request_params: 请求参数字典
        :return:
        :last_editors: HuangJianYi
        """
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        pay_order_model = PayOrderModel(db_transaction=db_transaction, context=self)
        refund_order_model = RefundOrderModel(db_transaction=db_transaction, context=self)
        try:
            db_transaction.begin_transaction()
            if req_info_dict["refund_status"] == "SUCCESS":
                self.logging_link_info(f'pay_order_no:{str(req_info_dict["out_trade_no"])},微信退款异步通知:' + str(req_info_dict))
                # 退款成功(相关表处理)
                refund_order_model.update_table("refund_status=3,out_refund_no=%s,refund_date=%s", where="refund_no=%s", params=[req_info_dict["refund_id"], req_info_dict["success_time"], req_info_dict["out_refund_no"]])
                pay_order_model.update_table("order_status=20,refund_amount=%s", where="pay_order_no=%s", params=[int(req_info_dict["settlement_refund_fee"]) / 100, req_info_dict["out_trade_no"]])
                db_transaction.commit_transaction()
            else:
                # 退款失败(只更新退款表)
                refund_order_model.update_table("refund_status=4", where="out_refund_no=%s", params=req_info_dict["refund_id"])
        except Exception as ex:
            db_transaction.rollback_transaction()
            self.logging_link_error("微信退款异步通知:数据处理异常:" + str(ex))