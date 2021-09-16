# -*- coding: utf-8 -*-
# @Time    : 2021/9/7 21:00
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : api.py

from djtesting.request import build


def call_api(method, url, type="urlencode", **kwargs):
    br = build.Build()
    return br.request(method=method, url=url, type=type, **kwargs)


def get(url, query_data=None, **kwargs):
    return call_api(method="get", url=url, query_data=query_data, **kwargs)


def post(url, data=None, **kwargs):
    return call_api("post", url, data=data, **kwargs)


def put(url, data=None, type="json", **kwargs):
    return call_api("put", url, data=data, type=type, **kwargs)


def delete(url, data=None, type="json", **kwargs):
    return call_api("delete", url, data=data, type=type, **kwargs)


if __name__ == '__main__':
    url = rf"http://dj.reconova.com?a=1"
    # print(get(url=url, type="urlencode", query_data={"chinablue":"djtest"},data={"chinablue":"djtest"}))
    # print(get(url=url, type="json", query_data={"chinablue":"djtest"},data={"chinablue":"djtest"}))
    # print(post(url=url, type="urlencode",data={"chinablue":"djtest"}))
    # print(post(url=url, type="json",data={"chinablue":"djtest"}))

    print(post(url=url, type="json", data={"chinablue": "djtest"}, headers={"djheaders": "111111"}))
