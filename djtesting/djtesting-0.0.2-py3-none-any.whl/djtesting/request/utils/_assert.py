# -*- coding: utf-8 -*-
# @Time    : 2021/9/13 17:03
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : _assert.py

import allure

from ._allure import allure_attach_text

def assert_actual_equal_expect(assert_desc, actual_value, expect_value):
    actual_value = str(actual_value)
    expect_value = str(expect_value)

    with allure.step(f"断言校验: {assert_desc}, 断言方式: 等于"):
        allure_attach_text(f"实际值: {actual_value}", "")
        allure_attach_text(f"期望值: {expect_value}", "")
        assert expect_value == actual_value










