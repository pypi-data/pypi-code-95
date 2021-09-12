#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import os

from edukit_sdk.edukit.common.constant.client_constant import ClientConstant
from edukit_sdk.edukit.common.constant.common_constant import CommonConstant


class Config:
    def get_config(self):
        rsp = dict()
        path = os.path.join(CommonConstant.ROOT_PATH,
                            CommonConstant.CONFIG_DIR, 'edukit_config.ini')
        config_str = self.file_get_contents(path)
        config_list = config_str.split(';')
        for config in config_list:
            single_config_list = config.split('=')
            if single_config_list[0] and single_config_list[1].strip():
                eventually_key = single_config_list[0].strip().replace(
                    '.', '_').upper()
                rsp[eventually_key] = single_config_list[1].strip()
        return rsp

    def get_domain(self):
        return self.get_config().get(ClientConstant.SERVER_DOMAIN)

    # 将文件内容读取到一个字符串中
    @staticmethod
    def file_get_contents(path):
        data = ''
        with open(path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                data += line
        return data
