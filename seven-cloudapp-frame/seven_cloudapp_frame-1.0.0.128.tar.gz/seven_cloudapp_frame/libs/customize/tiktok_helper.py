# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-01-14 10:44:07
@LastEditTime: 2021-09-08 10:01:23
@LastEditors: HuangJianYi
@Description: 
"""
import requests
import json
from Crypto.Cipher import AES
import base64
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_framework.base_model import *


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
        :last_editors: HuangJingCan
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
