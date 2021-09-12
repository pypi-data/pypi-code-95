#!/usr/bin/python
# encoding=utf-8

"""
@Author  :  Lijiawei
@Date    :  8/31/2021 9:42 PM
@Desc    :  Tools line.
"""
import base64
import subprocess
import re
from airtest.utils.logger import get_logger
from airtest.core.api import *
from airtest.core.android.adb import ADB
import os
import configparser

LOGGING = get_logger(__name__)


def allure_report(report_path, report_html):
    """生成allure 报告"""
    # 执行命令 allure generate
    allure_cmd = "allure generate %s -o %s --clean" % (report_path, report_html)
    try:
        subprocess.call(allure_cmd, shell=True)
    except Exception:
        LOGGING.error("执行用例失败，请检查一下测试环境相关配置")
        raise


def display():
    """
    获取当前设备的长宽
    :return:
    """
    width, height = device().get_current_resolution()
    return width, height


def dev_uri(state=None):
    """
    Perform `adb devices` command and return the list of adb devices
    :param state: optional parameter to filter devices in specific state
    :return: list od adb devices
    """
    patten = re.compile(r'^[\w\d.:-]+\t[\w]+$')
    device_list = []
    output = ADB().cmd("devices", device=False)
    for line in output.splitlines():
        line = line.strip()
        if not line or not patten.match(line):
            continue
        serialno, cstate = line.split('\t')
        if state and cstate != state:
            continue
        device_list.append(serialno)
    return device_list


def get_report(airtest_report_path):
    """
    获取最新测试report path
    :return: report name and path
    """
    file_lists = os.listdir(airtest_report_path)
    file_lists.sort(key=lambda fn: os.path.getmtime(airtest_report_path + "/" + fn)
                    if not os.path.isdir(airtest_report_path + "/" + fn) else 0)
    report = os.path.join(airtest_report_path, file_lists[-1])
    print(file_lists[-1])
    return report


def encryption(value):
    """
    加密
    :param value:
    :return:
    """
    bytes_url = value.encode("utf-8")
    str_url = base64.b64encode(bytes_url)
    return str_url


def decryption(value):
    """
    解密
    :param value:
    :return:
    """
    str_url = base64.b64decode(value).decode("utf-8")
    return str_url


class ReadConfig:
    """配置文件"""

    def __init__(self, ini_path):
        self.ini_path = ini_path
        if not os.path.exists(ini_path):
            raise FileNotFoundError("配置文件%s不存在！" % ini_path)
        self.config = configparser.RawConfigParser()  # 当有%的符号时请使用Raw读取
        self.config.read(ini_path, encoding='utf-8')

    def _get(self, section, option):
        """获取"""
        return self.config.get(section, option)

    def _set(self, section, option, value):
        """更新"""
        self.config.set(section, option, value)
        with open(self.ini_path, 'w') as f:
            self.config.write(f)

    def getvalue(self, env, name):
        return self._get(env, name)

    def update_value(self, env, name, value):
        return self._set(env, name, value)

