#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class ServiceErrorCode:
    def __init__(self, success=0, success_desc: str = "Operation success"):
        self.success = success
        self.success_desc = success_desc

    @staticmethod
    def get_error_code(self):
        """
        * 获取错误编码，后4位
        :return: 错误编码
        """
        pass

    @staticmethod
    def get_error_desc(self):
        """
        * 获取错误描述
        :return: 错误描述
        """
        pass
