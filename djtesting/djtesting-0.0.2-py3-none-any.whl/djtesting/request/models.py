# -*- coding: utf-8 -*-
# @Time    : 2021/9/3 14:22
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : models.py

from collections import Callable
from urllib.parse import urlparse, urlunparse

from .utils import common
from .hooks import default_hooks


class RequestHookMixin():
    def register_hook(self, event, hook):

        if event not in self.hooks:
            raise Exception(f"不支持的钩子事件: {event}")

        if isinstance(hook, Callable):
            self.hooks[event].append(hook)


class PrepareRequest(RequestHookMixin):

    def __init__(self):
        # 请求方法
        self.method = None
        # 请求地址
        self.url = None
        # 请求头
        self.headers = None
        # 请求数据
        self.body = None
        # 对内钩子
        self.hooks = default_hooks()

    # prepare参数为拼接出url的参数
    def prepare(self, method=None, url=None, headers=None, data=None, query_data=None, type=None, req_port=None,
                hooks=None):
        self.prepare_method(method)
        self.prepare_url(url=url, req_data=data, query_data=query_data, req_port=req_port)
        self.prepare_headers(headers)
        self.prepare_body(data, type)
        self.prepare_hooks(hooks)

    def __repr__(self):
        return f"<PreparedRequest [{self.method}]>"

    def prepare_method(self, method):
        self.method = method

        if self.method is not None:
            self.method = self.method.upper()

    def _url_path(self, url_path, req_data=None):
        import re
        vars_list = re.findall("{(.*?)}", url_path)

        if vars_list:
            if not req_data:
                raise Exception(f"url_path中存在变量, req_data参数不能为空")

            for tmp_key in vars_list:
                tmp_value = req_data.get(tmp_key)
                if not tmp_value:
                    raise Exception(f"req_data参数中需要{tmp_key}变量")

                url_path = url_path.replace(f"{{{tmp_key}}}", str(tmp_value))

        return url_path

    def _url_netloc(self, url_netloc, req_port=None):
        """
        :param url_netloc:
        :param req_port:
        :return:
        >>> PrepareRequest()._url_netloc("127.0.0.1")
        '127.0.0.1'
        >>> PrepareRequest()._url_netloc("localhost")
        'localhost'
        >>> PrepareRequest()._url_netloc("127.0.0.1:80")
        '127.0.0.1:80'
        >>> PrepareRequest()._url_netloc("localhost:80")
        'localhost:80'
        >>> PrepareRequest()._url_netloc("127.0.0.1", req_port=90)
        '127.0.0.1:90'
        >>> PrepareRequest()._url_netloc("localhost", req_port=90)
        'localhost:90'
        >>> PrepareRequest()._url_netloc("127.0.0.1:80", req_port=90)
        '127.0.0.1:90'
        >>> PrepareRequest()._url_netloc("localhost:80", req_port=90)
        'localhost:90'
        """
        if ":" in url_netloc:
            ip, port = url_netloc.split(":")
        else:
            ip, port = url_netloc, None

        if req_port:
            port = req_port

        url_netloc = f"{ip}:{port}" if port else f"{ip}"

        return url_netloc

    def _url_query(self, url_query, query_data):
        from urllib.parse import urlencode

        if query_data:
            if url_query:
                query = f"{url_query}&{urlencode(query_data)}"
            else:
                query = f"{urlencode(query_data)}"
        else:
            query = url_query

        return query

    def prepare_url(self, url, req_data=None, query_data=None, req_port=None):

        url = url.strip()

        # url必须以http开头
        if not url.lower().startswith(("http://", "https://")):
            raise Exception(f"raw_url必须以'http://'或'https://'开头, 当前url为: {url}")

        # 解析url
        try:
            scheme, netloc, path, params, query, fragment = urlparse(url)

        except:
            raise Exception(f"解析url失败: {url}")

        if not path:
            path = ""

        netloc = self._url_netloc(url_netloc=netloc, req_port=req_port)

        path = self._url_path(path, req_data)

        query = self._url_query(query, query_data)

        try:
            url_parts = [scheme, netloc, path, params, query, fragment]
            url = urlunparse(url_parts)
        except:
            raise Exception(f"url_parts拼接失败: {url_parts}")

        self.url = url

    def prepare_headers(self, headers):
        self.headers = {} if not self.headers else self.headers

        if headers:
            self.headers.update(headers)

    def prepare_body(self, data, type):

        # 如果请求参数为字典类型, 去除value为None的key
        if isinstance(data, dict):
            data = common.handle_request_data(data)

        body = None

        if type == "urlencode":
            body = data
        elif type == "json":
            self.headers["Content-Type"] = "application/json"
            import json
            body = json.dumps(data)
        elif type == "file":
            raise Exception
        else:
            raise Exception(f"当前type为: {type}")

        self.body = body

    def prepare_hooks(self, hooks):
        hooks = hooks or []
        for event in hooks:
            self.register_hook(event, hooks[event])


class Request(RequestHookMixin):
    _METHODS = ("GET", "POST", "PUT", "DELETE")
    _TYPE = ("urlencode", "json", "file")

    def __init__(self, method=None, url=None, headers=None, data=None, query_data=None, type=None, port=None,
                 hooks=None):
        # 部分参数需要设置默认值
        headers = {} if headers is None else headers
        # 请求头模拟一个真实的User-Agent
        headers.update(common.UserAgent().user_agent)

        data = {} if data is None else data

        # hooks函数
        hooks = {} if hooks is None else hooks
        # 将默认钩子赋值给 self.hook
        self.hooks = default_hooks()
        for k, v in hooks.items():
            self.register_hook(event=k, hook=v)
        # 将用户定义的钩子进行注册

        self.method = method
        self.url = url
        self.headers = headers
        self.data = data
        self.query_data = query_data
        self.type = type
        self.port = port

    def __repr__(self):
        return f"<Request [{self.method}]>"

    def prepare(self):
        p = PrepareRequest()
        p.prepare(
            method=self.method,
            url=self.url,
            headers=self.headers,
            data=self.data,
            query_data=self.query_data,
            type=self.type,
            req_port=self.port,
            hooks=self.hooks
        )

        return p


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)

    # from urllib.parse import urlencode
    #
    # url = "http://dj.reconova.com?a=1&b=2"
    # # url = "http://dj.reconova.com"
    # req_data = None
    # query_data = {"name": "chinablue", "age": "18"}
    #
    # pr = PrepareRequest()
    # pr.prepare_url(url=url, req_data=req_data, query_data=query_data)
    #
    # print(pr.url)
