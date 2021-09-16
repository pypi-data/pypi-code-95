# -*- coding: utf-8 -*-
# @Time    : 2021/9/9 11:47
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : utils.py

import datetime
from urllib.parse import parse_qs

import faker


class UserAgent():

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls.user_agent = {"User-Agent": str(faker.Factory().create("Zh_cn").user_agent())}

        return cls._instance


def querystring_to_dict(querystring):
    """
    :param querystring:
    :return:
    >>> querystring_to_dict("a=1")
    {'a': ['1']}
    >>> querystring_to_dict("a=1&b=2")
    {'a': ['1'], 'b': ['2']}
    >>> querystring_to_dict("a=1&b=2&a=11")
    {'a': ['1', '11'], 'b': ['2']}

    """

    return parse_qs(querystring)


def handle_request_data(data: dict):
    """
    处理请求参数:
        1. 移除data字典中value是None的key
        2. 如果value也是个字典，其中的None也会被移除。
        3. 如果value是一个长度为0的字符串, 则不会被过滤
    >>> handle_request_data({"name":"chinablue", "age":None})
    {'name': 'chinablue'}
    >>> handle_request_data({"name":"chinablue", "group":{"test":1, "dev":None}})
    {'name': 'chinablue', 'group': {'test': 1}}
    >>> handle_request_data({"name":"chinablue", "age":""})
    {'name': 'chinablue', 'age': ''}
    """

    keys_to_remove = []

    for k, v in data.items():

        if v is None:
            keys_to_remove.append(k)

        if isinstance(data[k], dict):
            handle_request_data(data[k])

    for k in keys_to_remove:
        del data[k]

    return data


def truncate_the_len_of_the_value(data: dict, threshold: int = 10000, truncate: int = 10, isCopy=True):
    """
    功能描述: 截取字典value的长度(针对字符串类型)
    :param data: 字典结构数据
    :param threshold: 设定截取阈值, 默认阈值为10000(即默认不截取)
    :param truncate: 截取后的长度, 默认截取后长度为10
    :param isCopy: 为了在递归中使用
    :return:
    >>> data = {"id1": "*"*5, "id2": "*"*30}
    >>> truncate_the_len_of_the_value(data)
    {'id1': '*****', 'id2': '******************************'}
    >>> data = {"id1": "*"*5, "id2": "*"*10}
    >>> truncate_the_len_of_the_value(data, threshold=5, truncate=1)
    {'id1': '*****', 'id2': '*'}
    >>> data = {"id1": "*"*30, "id2": {"i1": "*"*30, "i2": "*"*30}}
    >>> truncate_the_len_of_the_value(data, threshold=5)
    {'id1': '**********', 'id2': {'i1': '**********', 'i2': '**********'}}
    """

    if isCopy:
        import copy
        data = copy.deepcopy(data)

    if isinstance(data, dict):
        keys_to_handle = []

        for k, v in data.items():

            if isinstance(v, str):
                if len(v) > threshold:
                    keys_to_handle.append(k)

            if isinstance(v, dict):
                truncate_the_len_of_the_value(v, threshold=threshold, truncate=truncate, isCopy=False)

        for k in keys_to_handle:
            data[k] = data[k][:truncate]

        return data

    return data


def get_nowtime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=False)
