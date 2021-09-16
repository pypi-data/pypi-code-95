# -*- coding: utf-8 -*-
# @Time    : 2021/9/10 10:58
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : allure.py

from __future__ import absolute_import
import json

import allure

from ..log import Logger

logger = Logger()

def allure_attach_text(title, body):
    allure.attach(body=str(body), name=title, attachment_type=allure.attachment_type.TEXT)


def allure_attach_json(title, body):
    try:
        if isinstance(body, dict):
            body = json.dumps(body, sort_keys=True, indent=4, ensure_ascii=False)
            allure.attach(body=body, name=title, attachment_type=allure.attachment_type.JSON)
        else:
            raise Exception(f"body的数据类型必须为字典类型: {type(body)}")
    except Exception as e:
        logger.warning(f"body数据无法转为json串: ({type(body)}){body}")
        print(f"body数据无法转为json串: ({type(body)}){body}")
        allure_attach_text(title, body)
