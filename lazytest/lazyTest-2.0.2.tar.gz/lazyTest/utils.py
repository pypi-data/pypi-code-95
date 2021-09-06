# -*- coding = UTF-8 -*-
# Author   :buxiubuzhi
# File     : utils.py
# project  : Python_project
# time     : 2020/11/16 17:01
# Describe : 工具类
# ---------------------------------------

import datetime
import inspect
import os
import time
import functools




def Sleep(s: float = 1):
    """
    每个用例的强制休眠。
    """

    def Sleep(func):
        nonlocal s

        @functools.wraps(func)
        def inner(*args):
            time.sleep(s)
            result = func(*args)
            time.sleep(s)
            return result

        return inner

    return Sleep


class cls_Sleep:
    """
    脚本运行之前和脚本运行之后执行休眠操作
    可以提高脚本执行的稳定性
    """

    def __init__(self,s: float = 0.5):
        self.s = s

    def __call__(self, func_or_cls=None):
        if inspect.isfunction(func_or_cls):
            @functools.wraps(func_or_cls)
            def wrapper(*args, **kwargs):
                time.sleep(self.s)
                result = func_or_cls(*args, **kwargs)
                time.sleep(self.s)
                return result
            return wrapper
        elif inspect.isclass(func_or_cls):
            for name, func in list(func_or_cls.__dict__.items()):
                if inspect.isfunction(func):
                    setattr(func_or_cls, name, self(func))
            return func_or_cls
        else:
            raise AttributeError


def createData(body: str = "auto{}"):
    """
    返回给定字符串拼接上时间后的字符
    """
    nowTime = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M")[2:]
    return body.format(nowTime)


def getPorjectPath():
    """
    获取项目路径
    """
    return os.path.dirname(os.path.dirname(__file__))


def ClearTestResult(path: str):
    """
    清空目录中的文件
    参数：path：将会清除该目录下的所有文件，包括子目录文件；
    """
    for i in os.listdir(path):
        path_file = os.path.join(path, i)
        if os.path.isfile(path_file):
            os.remove(path_file)
        else:
            ClearTestResult(path_file)





