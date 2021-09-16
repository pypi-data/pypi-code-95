# -*- coding: utf-8 -*-
# @Time    : 2021/9/7 20:12
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : build_request.py

import urllib.parse
from binascii import b2a_hex
import json

import requests.api
from requests import Response

from .models import PrepareRequest, Request
from .utils.common import get_nowtime, truncate_the_len_of_the_value
from .log import Logger
from .utils.common import querystring_to_dict
from .hooks import default_hooks, dispatch_hook


class BaseBuild(object):
    # 请求超时
    timeout = 10

    # 日志开关
    verbose: bool = True

    # 默认截取的阈值
    allure_threshold = 10000

    # 默认截取后保留的长度
    allure_truncate = 10

    # 登录认证
    def certification(self):
        return {}

    # 数据解密
    def encryption(self):
        pass

    # 发送前钩子
    from requests import PreparedRequest
    def pre_send(self, pre_request: PreparedRequest):
        """
        功能: 向请求头,请求数据,查询字符串中添加额外信息
        其中:
            # 请求数据,数据类型可能是字典,字符串,字节
            data = pre_request.body
            # 请求头信息
            headers = pre_request.headers
            # 请求url
        url = pre_request.url
        :param pre_request:
        :return:
        """

        return pre_request

    def certification_auth(self):
        ...


class Build(BaseBuild):

    def __init__(self):
        # 默认的allure开关
        self.is_allure: bool = True

        # 抓取控制台日志到变量
        self.capture_console: bool = False

        # 接口的抓包信息
        self.capture_info: dict = {}

        # 默认进行接口http码断言
        self.is_assert = True

        # 登录凭证
        self.login_headers = {}

        # 事件钩子
        self.hooks = default_hooks()

    def merge_headers(self, dict_a: dict, dict_b: dict):
        dict_a.update(dict_b)
        return dict_a

    def prepare_request(self, request: Request):
        p = PrepareRequest()

        p.prepare(
            method=request.method.upper(),
            url=request.url,
            # TODO: 判断字典类型, 函数类型, 指定对象
            headers=self.merge_headers(request.headers, self.certification()),
            data=request.data,
            query_data=request.query_data,
            type=request.type,
            req_port=request.port,
            hooks=request.hooks
        )

        return p

    def request(
            self,
            method=None,
            url=None,
            headers=None,
            data=None,
            query_data=None,
            type=None,
            port=None,
            is_allure=True,
            timeout=None,
            capture_console=None,
            is_assert=True,
            hooks=None
    ):
        # 创建一个Request对象
        req = Request(
            method=method.upper(),
            url=url,
            headers=headers,
            data=data or {},
            query_data=query_data or {},
            type=type,
            port=port,
            hooks=hooks
        )

        self.prep = self.prepare_request(req)

        send_kwargs = {
            "is_allure": is_allure,
            "timeout": timeout if timeout else self.timeout,
            "verbose": self.verbose,
            "capture_console": capture_console,
            "is_assert": is_assert,
        }

        send_kwargs.update()

        resp = self.send(self.prep, **send_kwargs)

        return resp

    def send(self, pre_request: PrepareRequest, **kwargs):
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context

        verbose = kwargs.get("verbose")
        capture_console = kwargs.get("capture_console", self.capture_console)

        # 初始化日志类
        self.logger = Logger(verbose=verbose, capture_console=capture_console)

        is_allure = kwargs.get("is_allure", self.is_allure)
        allure_threshold = self.allure_threshold
        allure_truncate = self.allure_truncate

        is_assert = kwargs.get("is_assert", self.is_assert)
        timeout = kwargs.get("timeout")

        # api_desc字段是为了
        api_desc = kwargs.get("api_desc", "")

        # 请求前的钩子函数
        def hook_pre_send(pre_request, *args, **kwargs):

            self.pre_send(pre_request)

            return pre_request

        hooks = {"response": hook_pre_send}
        r = dispatch_hook('response', hooks, pre_request, **kwargs)

        try:
            self.capture_info["start_time"] = get_nowtime()
            r = requests.api.request(
                method=pre_request.method,
                url=pre_request.url,
                data=pre_request.body,
                headers=pre_request.headers,
                timeout=timeout,
                verify=False,
                hooks={"response": [self.capture_for_request_success, ]}
            )
        except Exception as e:
            # todo: 收集请求信息, 此时无响应信息
            self.capture_for_request_failure()
            self.capture_info["req_error"] = f"请求失败: {e}"

            if is_allure:
                capture_info_for_allure = truncate_the_len_of_the_value(
                    data=self.capture_info,
                    threshold=allure_threshold,
                    truncate=allure_truncate
                )

                from .utils._allure import allure_attach_json
                allure_attach_json(f"接口信息:{api_desc}", capture_info_for_allure)

            assert False, f"请求失败: {e}"

        # 请求后的钩子
        # hooks = pre_request.hooks

        # r.capture_info = self.capture_info

        if is_allure:
            capture_info_for_allure = truncate_the_len_of_the_value(
                data=self.capture_info,
                threshold=allure_threshold,
                truncate=allure_truncate
            )

            from .utils._allure import allure_attach_json
            allure_attach_json(f"接口信息:{api_desc}", capture_info_for_allure)

        if capture_console:
            r.get_console_data = self.logger.get_console_data()

        if is_assert:
            from .utils._objectpath import assert_json

            assert_json(
                desc="http状态码",
                json_data=getattr(r, "capture_info"),
                pattern="$.resp_code",
                expect_value=200
            )

        return r

    def _dict_to_json_log(self, data: dict):
        import json
        # TODO: 使用属性赋值的魔法函数来完成
        try:
            data = json.dumps(dict(data), indent=4, ensure_ascii=False)
        except:
            data = data
        return data

    def _handle_text(self, data: (str, bytes)):
        import json
        if isinstance(data, str):
            try:
                data = json.dumps(json.loads(data))
            except:
                ...
            return data

    def capture_for_request_success(self, resp: Response, *args, **kwargs):

        # 如果请求发送成功, 请求参数和响应参数均从Response对象中获取
        req_url = resp.request.url
        req_method = resp.request.method
        req_headers = resp.request.headers

        # todo: resp.request.body内容是什么类型?
        def _handle_req_data(body):
            # 如果是字符串
            self.logger.warning(f"resp.request.body数据: ({type(body)}){body}")
            if isinstance(body, str):
                body = querystring_to_dict(body)
                new_body = {}
                for k, v in body.items():
                    new_body[k] = v[0]
                body = new_body
            else:
                body = body

            return body

        req_data = _handle_req_data(resp.request.body)

        resp_code = resp.status_code
        resp_time = resp.elapsed.total_seconds()
        resp_headers = resp.headers

        # TODO: 能转字典就尽量转为字典格式
        resp_data = self._handle_text(resp.text)

        # 控制台打印
        self.logger.info(f"请求地址: ({req_method}){req_url}")
        self.logger.info(f"请求头: {self._dict_to_json_log(req_headers)}")  # 包含了请求类型
        self.logger.info(f"请求数据: {self._dict_to_json_log(req_data)}")

        self.logger.info(f"响应码: {resp_code}")
        self.logger.info(f"响应头: {self._dict_to_json_log(resp_headers)}")
        self.logger.info(f"响应数据: ({resp_time}){resp_data}")

        # 接口抓包
        self.capture_info["req_url"] = req_url
        self.capture_info["req_method"] = req_method
        self.capture_info["req_headers"] = req_headers

        self.capture_info["req_data"] = req_data

        self.capture_info["resp_time"] = resp_time
        self.capture_info["resp_code"] = resp_code
        self.capture_info["resp_headers"] = resp_headers
        self.capture_info["resp_data"] = resp_data

        # 为Response对象动态添加属性和方法
        resp.capture_info = self.capture_info

        from .utils._objectpath import assert_json
        import functools

        resp.assert_response = functools.partial(assert_json, json_data=self.capture_info)

        return resp

    def capture_for_request_failure(self):

        req_url = self.prep.url
        req_method = self.prep.method
        req_headers = self.prep.headers
        req_data = self.prep.body
        req_timeout = self.timeout

        # 控制台打印
        self.logger.error(f"请求地址: ({req_method}){req_url}")
        self.logger.error(f"请求头: {self._dict_to_json_log(req_headers)}")  # 包含了请求类型
        self.logger.error(f"请求数据: {self._dict_to_json_log(req_data)}")

        # 接口抓包
        self.capture_info["req_url"] = req_url
        self.capture_info["req_method"] = req_method
        # TODO: 报错情况下, 请求的headers是否有遗漏?
        self.capture_info["req_headers"] = req_headers
        self.capture_info["req_data"] = req_data
        self.capture_info["req_timeout"] = req_timeout

        return self.capture_info
