#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class AbstractErrorCode:
    @staticmethod
    def get_service_code():
        """
        获取服务编码，前4位
        :return:String 服务编码
        """
        return 0x3823

    def get_resp_error_code(self):
        """
        获取完整的错误码，高4位业务编码拼上低4位业务错误码
        :return: int 完整错误码
        """
        error_code = getattr(self, 'error_code')
        return (self.get_service_code() << 16) + error_code

    def get_hex_format_code(self):
        """
        获取完整的错误码的16进制编码输出
        :return:String 完整错误码
        """
        return hex(self.get_resp_error_code())

    def get_message(self):
        """
        获取错误描述信息，错误码+错误描述
        :return:String 描述信息
        """
        method = getattr(self, 'get_error_desc')
        return ''.join([self.get_hex_format_code(), ": ", ": ", method()])
