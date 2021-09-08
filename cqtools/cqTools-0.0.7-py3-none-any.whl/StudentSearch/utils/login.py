#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Author: 陈乾
#@Version: 1.0
#@Filename: login.py
#@Time: 2021/09/02 00:07
import json
import requests
from hashlib import sha256

class ReportLogin:
    def __init__(self) -> None:
        """用于健康上报平台的登录
        """
        self._session = requests.Session()
        self._headers = {
            'Connection': 'keep-alive',
            'Content-Type': "application/json;charset=UTF-8;Access-Control-Allow-Headers",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
        }
        self._message = None
        self._token = None

    def login(self, cardNo:str, password:str) -> dict:
        """登录健康上报平台，获取登录信息，可通过getMessage()方法获取详细信息
        :param: cardNo: 账号
        :param: password: 密码
        :return: 登录成功/密码错误/账号不存在或错误
        """
        loginUrl = "http://hmgr.sec.lit.edu.cn/wms/healthyLogin"
        data = {
            'cardNo': cardNo,
            'password': sha256(password.encode("utf-8")).hexdigest()
        }
        response = self._session.post(url=loginUrl, headers=self._headers, data=json.dumps(data), timeout=2)
        if response.json()['code'] == 200:
            self._token = response.json()['data']['token']
            return response.json()['data']
        else:
            raise Exception(response.json()['msg'])

    def _autologin(self) -> None:
        """获取学生权限token
        """
        self.login("B19041430", "123456cq")

    def resetPassword(self, cardNo:str) -> bool:
        """重置健康上报平台密码（123456）
        :param: cardNo: 需要重置的账号
        """
        try:
            self._autologin()
        except Exception:
            raise Exception("内置学生权限账号出错")
        resetUrl = f"http://hmgr.sec.lit.edu.cn/wms/initPassword?teamNo={cardNo}"
        resetHeaders = self._headers
        resetHeaders['token'] = self._token
        response = self._session.put(url=resetUrl, headers=resetHeaders, timeout=2)
        if response.json()['code'] == 200:
            return True
        else:
            return True

    def setPassword(self, cardNo:str, password:str, newPassword:str) -> bool:
        """修改密码
        :param: cardNo: 账号
        :param: password: 原密码
        :param: newPassword: 新密码
        """
        try:
            self.login(cardNo, password)
        except Exception:
            raise Exception("请提供正确的原账号密码")
        newPassword = sha256(newPassword.encode("utf-8")).hexdigest()
        url = f"http://hmgr.sec.lit.edu.cn/wms/password?password={newPassword}"
        headers = self._headers
        headers['token'] = self._token
        response = self._session.put(url, headers=headers, timeout=2)
        if response.json()['code'] == 200:
            return True
        else:
            return False