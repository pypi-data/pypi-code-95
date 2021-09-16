# -*- coding: utf-8 -*-
# @Time    : 2021/9/10 11:46
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : objectpath.py

from __future__ import absolute_import

# 输入数据必须是字典,或者可以转为字典
# 提取内容如果为多个,强制转为列表对象
# 当提取到的数据为None是, 是否抛出异常

import objectpath
import allure

from types import GeneratorType as generator
from itertools import chain

from ._assert import assert_actual_equal_expect


def parse_by_objectpath(data: (dict, str), pattern, res_allowNone=False, res_firstOne=True):
    """
    功能: 从复杂json中提取数据
    :param data: json数据
    :param pattern: 提取表达式
    :param res_allowNone: 是否允许提取不到信息, 默认False
    :param res_firstOne: 如果返回的是一个非空列表, 是否返回列表的首个元素, 默认False
    :return:
    >>> data = {"name": "chinablue", "age": 20}
    >>> parse_by_objectpath(data, "")
    Traceback (most recent call last):
    ...
    AssertionError: [提取失败]提取数据:{'name': 'chinablue', 'age': 20}, 提取表达式:
    >>> parse_by_objectpath(data, "$.name")
    'chinablue'
    >>> parse_by_objectpath(data, "$.age")
    20
    >>> parse_by_objectpath(data, "$..name")
    'chinablue'
    >>> parse_by_objectpath(data, "$..name", res_firstOne=False)
    ['chinablue']
    >>> parse_by_objectpath(data, "$..*[@.name]")
    'chinablue'
    >>> parse_by_objectpath(data, "$..*[@.name is 'chinablue'].age")
    20
    >>> data = '{"name": "chinablue", "age": 20}'
    >>> parse_by_objectpath(data, "$.name")
    'chinablue'
    >>> parse_by_objectpath(data, "$.name1")
    Traceback (most recent call last):
    ...
    AssertionError: [提取失败]提取数据:{'name': 'chinablue', 'age': 20}, 提取表达式:$.name1
    >>> parse_by_objectpath(data, "$.name1", res_allowNone=True)
    False
    >>> data = {"group": [{"name":"g1"},{"name":"g2"}]}
    >>> parse_by_objectpath(data, "count($..*[@.name])")
    2
    """

    if isinstance(data, str):
        data = objectpath.Tree({}).execute(data)

    if not isinstance(data, dict):
        assert False, f"[提取失败]输入参数d有误: {data}"

    with allure.step(f"提取表达式: {pattern}"):

        try:
            tree = objectpath.Tree(obj=data)

            r = tree.execute(pattern)

            if isinstance(r, (generator, chain)):
                res_list = list(r)
                if len(res_list) > 0:
                    if res_firstOne:
                        return res_list[0]
                    return res_list
                else:
                    if res_allowNone:
                        return False
                    assert False, f"[提取失败]提取数据:{data}, 提取表达式:{pattern}"
            else:
                if r is None:
                    if res_allowNone:
                        return False
                    assert False, f"[提取失败]提取数据:{data}, 提取表达式:{pattern}"
                return r

        except Exception as e:

            assert False, f"[提取失败]提取数据:{data}, 提取表达式:{pattern}"


def assert_json(desc, json_data, pattern, expect_value=None, res_firstOne=True):
    with allure.step(f"检查点: {desc}"):
        actual_value = parse_by_objectpath(
            data=json_data,
            pattern=pattern,
            res_firstOne=res_firstOne
        )

        if expect_value is not None:
            assert_actual_equal_expect(
                assert_desc=desc,
                actual_value=actual_value,
                expect_value=expect_value
            )

        return actual_value


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=False)

    # data = {"name": "chinablue", "age": 20}
    # res = parse_by_objectpath(data, "")
    # print(res)
