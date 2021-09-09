# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-01-14 10:44:07
@LastEditTime: 2021-09-08 19:32:23
@LastEditors: HuangJianYi
@Description: 
"""
import requests
import json
import hashlib
from Crypto.Cipher import AES
import base64
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_framework.base_model import *
from seven_cloudapp_frame.models.seven_model import InvokeResultData


class TikTokHelper:
    """
    :description: 抖音帮助类 1.临时登录凭证校验获取open_id、session_key  2.解析加密数据
    """
    logger_error = Logger.get_logger_by_name("log_error")

    @classmethod
    def code2_session(self, code="", anonymous_code=""):
        """
        :description:获取open_id、session_key等信息
        :param code: 登录票据,非匿名需要 code
        :param anonymous_code: 非匿名下的 anonymous_code 用于数据同步，匿名需要 anonymous_code
        :return: 
        :last_editors: HuangJianYi
        """
        redis_key = "tiktok_login_code:" + str(code)
        redis_init = SevenHelper.redis_init()
        code2_session_dict = redis_init.get(redis_key)
        if code2_session_dict:
            code2_session_dict = SevenHelper.json_loads(code2_session_dict)
            return code2_session_dict
        app_id = config.get_value("app_id")
        app_secret = config.get_value("app_secret")
        param = {
            'code': code,  # 用户点击按钮跳转到抖音授权页, 抖音处理完后重定向到redirect_uri, 并给我们加上code=xxx的参数, 这个code就是我们需要的
            'appid': app_id,
            'secret': app_secret,
            'anonymous_code': anonymous_code,
        }

        # 通过code获取access_token
        requset_url = 'https://developer.toutiao.com/api/apps/jscode2session'
        resp = None
        try:
            resp = requests.get(requset_url, params=param)
            res_result = json.loads(resp.text)
            open_id = res_result['openid']
            session_key = res_result['session_key']
            redis_init.set(redis_key, SevenHelper.json_dumps(res_result), ex=60 * 60)
            redis_init.set(f"tiktok_sessionkey:{str(open_id)}", session_key, ex=60 * 60)
            return res_result
        except Exception as ex:
            self.logger_error.error(str(ex) + "【code2_session】" + str(resp.text))
            return {}

    @classmethod
    def decrypt_data_by_code(self, open_id, code, encrypted_Data, iv):
        """
        :description:解析加密数据，客户端判断是否登录状态，如果登录只传open_id不传code，如果是登录过期,要传code重新获取session_key
        :param open_id：open_id
        :param code：登录票据
        :param encrypted_Data：加密数据,抖音返回加密参数
        :param iv：抖音返回参数
        :return: 解密后的数据，用户信息或者手机号信息
        :last_editors: HuangJianYi
        """
        data = {}
        if code:
            code2_session_dict = self.code2_session(code)
            if code2_session_dict:
                open_id = code2_session_dict["openid"]
        try:
            session_key = SevenHelper.redis_init().get(f"tiktok_sessionkey:{str(open_id)}")
            app_id = config.get_value("app_id")
            data_crypt = TikTokBizDataCrypt(app_id, session_key)
            data = data_crypt.decrypt(encrypted_Data, iv)  #data中是解密的信息
        except Exception as ex:
            self.logger_error.error(str(ex) + "【decrypt_data_by_code】")

        return data

    @classmethod
    def decrypt_data(self, app_id, session_key, encrypted_Data, iv):
        """
        :description:解析加密数据
        :param app_id: 抖音小程序标识
        :param session_key: session_key调用登录接口获得
        :param encrypted_Data：加密数据,抖音返回加密参数
        :param iv：抖音返回参数
        :return: 解密后的数据，用户信息或者手机号信息
        :last_editors: HuangJianYi
        """
        data = {}
        try:
            data_crypt = TikTokBizDataCrypt(app_id, session_key)
            #data中是解密的信息
            data = data_crypt.decrypt(encrypted_Data, iv)
        except Exception as ex:
            self.logger_error.error(str(ex) + "【decrypt_data】")
        return data


class TikTokBizDataCrypt:
    def __init__(self, app_id, session_key):
        self.app_id = app_id
        self.session_key = session_key

    def decrypt(self, encryptedData, iv):
        """
        :description: 解密
        :param encryptedData: encryptedData
        :param iv: iv
        :return str
        :last_editors: HuangJianYi
        """
        # base64 decode
        session_key = base64.b64decode(self.session_key)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)
        decrypted = {}
        cipher = AES.new(session_key, AES.MODE_CBC, iv)
        result_data = str(self._unpad(cipher.decrypt(encryptedData)), "utf-8")
        if result_data:
            decrypted = json.loads(result_data)
        if decrypted:
            if decrypted['watermark']['appid'] != self.app_id:
                raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]


class TikTokPayRequest(object):
    """配置账号信息"""
    # =======【基本信息设置】=====================================
    # 抖音公众号身份的唯一标识。审核通过后，在抖音发送的邮件中查看
    app_id = ""
    # API密钥，需要在商户后台设置
    api_key = ""
    #开发者自定义字段，回调原样回传
    cp_extra = ""
    #商户自定义回调地址
    notify_url = ""
    #担保交易Token（令牌）
    token = ""
    #担保交易盐值
    salt = ""
    # 日志
    logger_error = Logger.get_logger_by_name("log_error")

    def __init__(self):
        """
        :description: 初始化
        :last_editors: HuangJianYi
        """
        payconfig = config.get_value("tiktok_pay")
        self.app_id = config.get_value("app_id")
        self.api_key = payconfig['api_key']
        self.cp_extra = payconfig['cp_extra']
        self.notify_url = payconfig['notify_url']
        self.token = payconfig['token']
        self.salt = payconfig['salt']

    def create_order(self, total_amount=1, subject="", body="", valid_time=900, thirdparty_id="", disable_msg=None, msg_page="", store_uid=""):
        """
        :description: 服务端创建预下单
        :param total_amount:支付价格; 接口中参数支付金额单位为[分]|默认 1
        :param subject: 商品描述; 长度限制 128 字节，不超过 42 个汉字 |默认 自己约定一个比如 “福小宠商品”*|
        :param body:商品详情|默认 自己约定一个比如 “福小宠商品”
        :param valid_time:订单过期时间(秒); 最小 15 分钟，最大两天|默认 900
        :param thirdparty_id:服务商模式接入必传,第三方平台服务商 id，非服务商模式留空|默认传空字符串
        :param disable_msg:是否屏蔽担保支付的推送消息，1-屏蔽 0-非屏蔽，接入 POI 必传|默认传None
        :param msg_page:担保支付消息跳转页|默认传空字符串
        :param store_uid:多门店模式下必传,多门店模式下，门店 uid|默认传空字符串
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            app_id = self.app_id
            #out_order_no 开发者服务端的唯一订单号
            out_order_no = SevenHelper.create_order_id()
            #回调地址
            notify_url = self.notify_url
            cp_extra = self.cp_extra
            # 在这里将订单信息存入数据库

            data = {}
            data['out_order_no'] = out_order_no
            data['cp_extra'] = cp_extra
            data['notify_url'] = notify_url
            data['total_amount'] = str(int(decimal.Decimal(str(total_amount)) * 100))
            data['subject'] = subject
            data['body'] = body
            data['valid_time'] = valid_time
            if disable_msg:
                data['disable_msg'] = int(disable_msg)
            if msg_page:
                data['msg_page'] = msg_page
            if store_uid:
                data['store_uid'] = store_uid

            sign = self.get_tt_sign(data)
            # 如果有第三方平台服务商id:thirdparty_id字段请把他放入data的字典里面
            data['sign'] = sign
            data['app_id'] = app_id

            if thirdparty_id:
                data['thirdparty_id'] = thirdparty_id

            redis_key = "tiktok_order_id:" + str(out_order_no)
            order_id = SevenHelper.redis_init().get(redis_key)
            if order_id:
                invoke_result_data.data = order_id
                return invoke_result_data

            url = "https://developer.toutiao.com/api/apps/ecpay/v1/create_order"
            headers = {"Content-type": "application/json"}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                resp = json.loads(response.text)
                # err_no	number	    状态码 0-业务处理成功
                # err_tips	string	    错误提示信息，常见错误处理可参考附录常见问题章节
                # data	    orderInfo	拉起收银台的 orderInfo
                # {"err_no": 2000, "err_tips": "单号记录不存在", "data": null}
                if resp['err_no'] == 0:
                    order_id = str(resp['data']['order_id'])
                    SevenHelper.redis_init().set(redis_key, order_id, ex=3600 * 1)
                    invoke_result_data.data = order_id
                    return invoke_result_data
                else:
                    self.logger_error.error(f"【{out_order_no},创建预下单】" + resp['err_tips'])
                    invoke_result_data.success = False
                    invoke_result_data.error_code="error"
                    invoke_result_data.error_message = resp['err_tips']
                    return invoke_result_data
            else:
                self.logger_error.error(f"【{out_order_no},创建预下单】" + response.text)
                invoke_result_data.success = False
                invoke_result_data.error_code="error"
                invoke_result_data.error_message = "支付接口报错，请重试"
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【创建预下单】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code="error"
            invoke_result_data.error_message = "创建预下单出现异常，请重试"
            return invoke_result_data

    def query_order(self, out_order_no="", thirdparty_id=""):
        """
        :description: 查询订单
        :param out_order_no：开发者侧的订单号, 不可重复
        :param thirdparty_id: 服务商模式接入必传  第三方平台服务商 id，非服务商模式留空字符串|默认值 空字符串
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            app_id = self.app_id
            data = {}
            data['out_order_no'] = out_order_no
            sign = self.get_tt_sign(data)
            data['sign'] = sign
            data['app_id'] = app_id
            if thirdparty_id:
                data['thirdparty_id'] = thirdparty_id

            url = "https://developer.toutiao.com/api/apps/ecpay/v1/query_order"
            headers = {"Content-type": "application/json"}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                resp = json.loads(response.text)
                # {"err_no": 2000, "err_tips": "单号记录不存在", "out_order_no": "", "order_id": "", "payment_info": null}
                # payment_info 返回值结构如下：
                # {
                #     "total_fee": 1200,
                #     "order_status": "PROCESSING-处理中|SUCCESS-成功|FAIL-失败|TIMEOUT-超时",
                #     "pay_time": "支付时间",
                #     "way": 1,
                #     "channel_no": "渠道单号",
                #     "channel_gateway_no": "渠道网关号"
                # }
                if resp['err_no'] == 0:
                    invoke_result_data.data = resp
                    return invoke_result_data
                else:
                    self.logger_error.error(f"【{out_order_no},查询订单】" + resp['err_tips'])
                    invoke_result_data.success = False
                    invoke_result_data.error_code="error"
                    invoke_result_data.error_message = resp['err_tips']
                    return invoke_result_data
            else:
                self.logger_error.error(f"【查询订单】" + response.text)
                invoke_result_data.success = False
                invoke_result_data.error_code="error"
                invoke_result_data.error_message = "查询订单出现异常，请重试"
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【查询订单】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code="error"
            invoke_result_data.error_message = "查询订单出现异常，请重试"
            return invoke_result_data

    def create_refund(self, out_order_no="", refund_amount=1, reason="", thirdparty_id="", disable_msg=None, msg_page="", all_settle=None):
        """
        :description: 服务端退款请求
        :param out_order_no:商户分配订单号，标识进行退款的订单，开发者服务端的唯一订单号
        :param refund_amount: 退款金额，单位[分]|默认 1
        :param reason:退款理由，长度上限 100|默认 由开发者定 例如：“7天无理由退款”
        :param thirdparty_id:服务商模式接入必传,第三方平台服务商 id，非服务商模式留空|默认传空字符串
        :param disable_msg:是否屏蔽担保支付的推送消息，1-屏蔽 0-非屏蔽，接入 POI 必传|默认传None
        :param msg_page:担保支付消息跳转页|默认传空字符串
        :param all_settle:是否为分账后退款，1-分账后退款；0-分账前退款。分账后退款会扣减可提现金额，请保证余额充足*|默认传None
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            app_id = self.app_id
            #out_order_no 开发者服务端的唯一订单号
            out_refund_no = SevenHelper.create_order_id()
            #回调地址
            notify_url = self.notify_url
            cp_extra = self.cp_extra
            # 在这里将订单信息存入数据库
            data = {}
            data['out_refund_no'] = out_refund_no
            #cp_extra 开发者自定义字段，回调原样回传
            data['cp_extra'] = cp_extra
            data['notify_url'] = notify_url
            data['out_order_no'] = out_order_no
            data['refund_amount'] = str(int(decimal.Decimal(str(refund_amount)) * 100))
            data['reason'] = reason
            if disable_msg:
                data['disable_msg'] = int(disable_msg)
            if msg_page:
                data['msg_page'] = msg_page
            if all_settle:
                data['all_settle'] = int(all_settle)

            sign = self.get_tt_sign(data)
            # 如果有第三方平台服务商 id :thirdparty_id字段请把他放入data.update的字典里面
            data['sign'] = sign
            data['app_id'] = app_id
            if thirdparty_id:
                data['thirdparty_id'] = thirdparty_id

            url = "https://developer.toutiao.com/api/apps/ecpay/v1/create_refund"
            headers = {"Content-type": "application/json"}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                resp = json.loads(response.text)
                if resp['err_no'] == 0:
                    invoke_result_data.data = resp
                    return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【退款】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "退款出现异常，请重试"
            return invoke_result_data


    def query_refund(self, out_refund_no="", thirdparty_id=""):
        """
        :desciption:退款查询
        :param out_refund_no:开发者侧的退款单号, 不可重复
        :param thirdparty_id:服务商模式接入必传  第三方平台服务商 id，非服务商模式留空字符串
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            app_id = self.app_id
            data = {}
            data['out_refund_no'] = out_refund_no
            sign = self.get_tt_sign(data)
            data['sign'] = sign
            data['app_id'] = app_id
            if thirdparty_id:
                data['thirdparty_id'] = thirdparty_id

            url = "https://developer.toutiao.com/api/apps/ecpay/v1/query_refund"
            headers = {"Content-type": "application/json"}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                resp = json.loads(response.text)
                if resp['err_no'] == 0:
                    invoke_result_data.data = resp
                    return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【退款查询】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "退款查询出现异常，请重试"
            return invoke_result_data

    def create_settle(self, out_order_no="", settle_desc="", settle_params="", thirdparty_id=""):
        """
        :description:服务端结算请求
        :param out_order_no:商户分配订单号，标识进行退款的订单，开发者服务端的唯一订单号
        :param settle_desc:结算描述 默认 自己约定一个比如 “福小宠商品结算”
        :param settle_params:其他分账方信息，分账分配参数 SettleParameter 数组序列化后生成的 json 格式字符串
        :param thirdparty_id：服务商模式接入必传,第三方平台服务商 id，非服务商模式留空|默认传空字符串
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            app_id = self.app_id
            #out_order_no 开发者服务端的唯一订单号
            out_settle_no = SevenHelper.create_order_id()
            #回调地址
            notify_url = self.notify_url
            cp_extra = self.cp_extra
            # 在这里将分账信息存入数据库
            data = {}
            data['out_settle_no'] = out_settle_no
            #cp_extra 开发者自定义字段，回调原样回传
            data['cp_extra'] = cp_extra
            data['notify_url'] = notify_url
            data['out_order_no'] = out_order_no
            data['settle_desc'] = settle_desc
            if settle_params:
                data['settle_params'] = settle_params
            sign = self.get_tt_sign(data)
            data['sign'] = sign
            data['app_id'] = app_id
            if thirdparty_id:
                data['thirdparty_id'] = thirdparty_id

            url = "https://developer.toutiao.com/api/apps/ecpay/v1/settle"
            headers = {"Content-type": "application/json"}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                resp = json.loads(response.text)
                if resp['err_no'] == 0:
                    invoke_result_data.data = resp
                    return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【结算请求】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "结算请求出现异常，请重试"
            return invoke_result_data

    def query_settle(self, out_settle_no="", thirdparty_id=""):
        """
        :desciption:结算查询
        :param out_settle_no:开发者侧的分账号, 不可重复
        :param thirdparty_id:服务商模式接入必传  第三方平台服务商 id，非服务商模式留空字符串
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            app_id = self.app_id
            data = {}
            data['out_settle_no'] = out_settle_no
            sign = self.get_tt_sign(data)
            data['sign'] = sign
            data['app_id'] = app_id
            if thirdparty_id:
                data['thirdparty_id'] = thirdparty_id

            url = "https://developer.toutiao.com/api/apps/ecpay/v1/query_settle"
            headers = {"Content-type": "application/json"}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                resp = json.loads(response.text)
                if resp['err_no'] == 0:
                    invoke_result_data.data = resp
                    return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【结算查询】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "结算查询出现异常，请重试"
            return invoke_result_data

    def get_tt_sign(self, params):
        """
        :description: 获取头条请求sign
        :param params: 参数字典
        :return: sign
        :last_editors: HuangJianYi
        """
        params_copy = copy.deepcopy(params)
        for key, value in params_copy.items():
            if isinstance(value, int):
                params_copy[key] = str(value)
        params_copy['salt'] = self.salt
        # params_copy['salt'] = 'your_payment_salt'
        params_list = sorted(list(params_copy.items()), key=lambda x: x[1])
        params_str = ''.join(f"{v}&" for k, v in params_list)[:-1]
        sign = hashlib.md5(params_str.encode('utf-8')).hexdigest()
        return sign


class TikTokReponse(object):
    """
    :description: 抖音支付响应类 根据支付/退款/分账等回调json内容，检测type字段判断是支付回调还是退款回调，type:payment 支付成功回调,refund退款成功回调,settle分账成功回调
    """
    logger_error = Logger.get_logger_by_name("log_error")

    def __init__(self, data):
        self.data = data  #data由json.loads(self.request.body)获得
        payconfig = config.get_value("tiktok_pay")
        self.token = payconfig['token']

    def check_sign(self):
        """
        :description: 校验签名
        :return:
        :last_editors: HuangJianYi
        """
        #计算服务端sign
        service_signature = self.get_tt_callback_sign(self.data)
        #验证成功,进行业务处理
        log_msg = f'客户端签名:{self.data["msg_signature"]},服务端签名:{service_signature}'
        # self.logger_error.error(log_msg)
        if service_signature == self.data["msg_signature"]:
            return True
        else:
            return False

    def get_tt_callback_sign(self, params):
        """
        :description: 获取头条回调sign
        :param params: 参数字典
        :return: sign
        :last_editors: HuangJianYi
        """
        keys = ['type', 'msg_signature']
        params_copy = {key: params[key] for key in params if key not in keys}
        for key, value in params_copy.items():
            if isinstance(value, int):
                params_copy[key] = str(value)
        params_copy['token'] = self.token
        # params_copy['salt'] = 'your_payment_salt'
        params_list = sorted(list(params_copy.items()), key=lambda x: x[1])
        params_str = ''.join(f"{v}" for k, v in params_list)
        sign = CryptoHelper().sha1_encrypt(params_str)
        return sign