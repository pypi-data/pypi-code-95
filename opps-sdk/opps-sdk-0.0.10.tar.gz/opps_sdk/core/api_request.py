import json

import requests

from opps_sdk.core.log_util import log_error, log_info
from opps_sdk.core.param_handler import replace_none_to_empty
from opps_sdk.core.rsa_utils import rsa_sign, rsa_design


class ApiRequest:
    """
    网络请求类
    """
    base_url = ''
    product_id = ''
    huifu_id = ''
    url = ''
    request_params = {}
    version = ''
    private_key = ''
    public_key = ''
    connect_timeout = ''

    @staticmethod
    def build(product_id, private_key, public_key, url, request_params, huifu_id, connect_timeout=30):
        """
        初始化 网络请求类
        :param product_id: 产品号
        :param private_key: 私钥
        :param public_key: 公钥
        :param url: 请求地址
        :param request_params: 请求参数
        :param connect_timeout: 超时时间
        :return: 网络请求类
        """
        ApiRequest.product_id = product_id
        ApiRequest.url = url
        ApiRequest.huifu_id = huifu_id
        ApiRequest.private_key = private_key
        ApiRequest.public_key = public_key
        ApiRequest.request_params = request_params
        ApiRequest.version = "1.0.0"
        ApiRequest.connect_timeout = connect_timeout

    @staticmethod
    def post(request_file=None):
        return ApiRequest._request('post', request_file)

    @staticmethod
    def get():
        return ApiRequest._request('get')

    @staticmethod
    def _build_request_info(url, method, params, files):
        """
        根据请求方式构造请求头和请求参数
        :param url: 请求地址
        :param method: 请求方法，post or get
        :param params: 请求参数
        :param files: 请求文件
        :return: header 请求头 params 请求参数
        """

        # 构造请求头
        header = {'product_id': ApiRequest.product_id,
                  "format": 'JSON',
                  'charset': 'UTF-8',
                  'version': ApiRequest.version
                  }

        # 构造请求体

        body = dict()
        body["sys_id"] = ApiRequest.huifu_id
        body["sign_type"] = "RSA2"

        datastr = ""

        if params is not None:
            params = replace_none_to_empty(params)
            datastr = json.dumps(params)

        # 获取商户密钥
        if not ApiRequest.private_key:
            raise RuntimeError('privite_key is none')

        # 对请求参数进行加签
        flag, sign = rsa_sign(ApiRequest.private_key, datastr, 'utf-8')

        if not flag:
            log_error('request to {}, sign error {} '.format(url, rsa_sign))

        # 将签名更新到请求头中
        body['sign'] = sign
        body['data'] = datastr

        return header, body

    @staticmethod
    def _request(method, files=None):
        """
        执行请求
        :param method: 请求方法类型

        :param files: 上传的文件
        :return: 网路请求返回的数据
        """

        request_url = ApiRequest.base_url + ApiRequest.url

        header, params = ApiRequest._build_request_info(request_url, method, ApiRequest.request_params, files)

        http_method = getattr(requests, method or 'post')

        if files:
            resp = http_method(request_url, data=params, files=files, timeout=ApiRequest.connect_timeout,
                               headers=header)

        elif method == 'post':
            resp = http_method(request_url, json=params, files=files, timeout=ApiRequest.connect_timeout,
                               headers=header)

        else:
            resp = http_method(request_url, params, timeout=ApiRequest.connect_timeout, headers=header)

        log_info('request to {}\nheader={}\nrequest_params{} \nresp is {}'.format( request_url,header, params, resp.text))
        return ApiRequest._build_return_data(resp)

    @staticmethod
    def _build_return_data(resp):
        """
        解析网络返回
        :param resp: response
        :return: 解析处理后的网络返回
        """

        try:
            resp_json = json.loads(resp.text)
        except Exception as e:
            log_error('resp_code is ' + str(resp.status_code))
            log_error(str(e))
            return resp.text

        # 服务端返回数据
        data = resp_json.get('data', '')
        # 返回字段中的签名
        resp_sign = resp_json.get('sign', '')

        if not resp_sign:
            # 如果没有签名字段，直接返回内容，一般为404等
            return resp_json

        # 当业务请求成功时验证返回数据与签名
        if not ApiRequest.public_key:
            raise RuntimeError('public_key is none')

        # 验证返回数据与返回加签结果是否一致
        flag, info = rsa_design(resp_sign, data, ApiRequest.public_key)

        if not flag:
            # 如果验签失败，抛出异常
            log_error('check signature error !'.format(info))
            raise RuntimeError(info)

        return json.loads(data)
