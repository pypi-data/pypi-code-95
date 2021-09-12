#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import hashlib
import importlib
import logging
import mimetypes
import os

from edukit_sdk.edukit.common.constant.common_constant import CommonConstant
from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.model.result import Result


class Helpers:
    @staticmethod
    def get_root():
        return os.path.join(os.getcwd(), '..', '..', '..', '..')

    @staticmethod
    def get_file_dir_name(path):
        path = path if path else ''
        return os.path.split(path)[0]

    @staticmethod
    def get_file_base_name(path):
        path = path if path else ''
        return os.path.split(path)[1]

    @staticmethod
    def get_file_name(path):
        path = path if path else ''
        return os.path.splitext(Helpers.get_file_base_name(path))[0]

    @staticmethod
    def get_file_extension(path):
        path = path if path else ''
        return os.path.splitext(Helpers.get_file_base_name(path))[1]

    @staticmethod
    def get_file_size(path):
        return os.path.getsize(path)

    @staticmethod
    def get_sha256(path):
        h = hashlib.sha256()
        with open(path, 'rb') as file:
            chunk = 0
            while chunk != b'':
                # read only 1024 bytes at a time
                chunk = file.read(1024)
                h.update(chunk)

        # 返回摘要的十六进制表示
        return h.hexdigest()

    @staticmethod
    def get_mime(path):
        return mimetypes.guess_type(path)[0]

    @staticmethod
    def build_error_result(errcode):
        result = Result()
        common_error_code = CommonErrorCode(errcode)
        result.result_code = common_error_code.get_resp_error_code()
        result.result_desc = common_error_code.error_desc
        return result

    @staticmethod
    def change_object_to_array(obj):
        object_to_array_list = dict()
        if vars(obj).items():
            for name, value in vars(obj).items():
                method_value_list = list()
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, '__dict__'):
                            method_value_list.append(
                                Helpers.change_object_to_array(item))
                        else:
                            method_value_list.append(item)
                else:
                    if hasattr(value, '__dict__'):
                        method_value_list.append(
                            Helpers.change_object_to_array(value))
                    else:
                        method_value_list.append(value)
                server_name = Helpers.change_to_server_name(name)
                if isinstance(value, list):
                    object_to_array_list[server_name] = method_value_list
                else:
                    object_to_array_list[server_name] = method_value_list[0] \
                        if len(method_value_list) == 1 else method_value_list

        return object_to_array_list

    @staticmethod
    def parse_response(response, obj_name: str):
        path, class_name = str(obj_name).rsplit('.', 1)
        package = importlib.import_module(path)
        method = getattr(package, class_name)
        obj = method()
        if obj:
            property_name_list = [
                k[1:] if k[:1] == '_' else k for k in obj.__dict__.keys()
            ]
        if response:
            logging.info(response)
            for k, v in response.items():
                Helpers.set_attr(k, v, property_name_list, obj)
        return obj

    @staticmethod
    def is_success(result):
        result_code = result.get('result').get('resultCode')
        return True if result_code is not None and \
                       result_code == CommonConstant.RESULT_SUCCESS else False

    @staticmethod
    def build_result(rsp):
        logging.info(rsp)
        result = rsp.get('result')
        result_obj = Result()
        result_obj.result_code = result.get('resultCode')
        result_obj.result_desc = result.get('resultDesc')
        return result_obj

    @staticmethod
    def has_empty_param(param):
        for item in param:
            if not item:
                return True
        return False

    @staticmethod
    def set_attr(name, value, property_name_list, obj):
        if name != 'result':
            for item in property_name_list:
                if item.replace('_', '').lower() == name.lower():
                    setattr(obj, item, value)
        else:
            result = Result()
            result.result_code = value.get('resultCode')
            result.result_desc = value.get('resultDesc')
            setattr(obj, 'result', result)

    @staticmethod
    def change_to_server_name(name: str):
        server_name = ''
        if name:
            name_list = name.split('_')
            for item in name_list:
                if server_name:
                    server_name += item.capitalize()
                else:
                    server_name += item
        return server_name
