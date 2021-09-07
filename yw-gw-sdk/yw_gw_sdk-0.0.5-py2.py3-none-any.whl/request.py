import datetime
from .conf_parser import new_conf
from urllib.parse import urlparse
from .exception import RequestError
from .signer import hmac_signer
from urllib.parse import urljoin
import requests

GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'

init_conf = new_conf()


def gmt() -> str:
    return datetime.datetime.utcnow().strftime(GMT_FORMAT)


class HttpRequest:
    conf = init_conf

    def __init__(self, method: str, uri: str, extend_headers: dict = None, body=None):
        self.method = method.upper()
        self.uri = uri
        self.date = gmt()
        self.url_parse = urlparse(self.uri)
        self.extend_headers = extend_headers
        self.body = body if body else None

    def get_access_key(self):
        return self.conf.access_key

    def get_hash_strategy(self):
        return self.conf.hash_strategy

    def get_path(self):
        return self.url_parse.path

    def get_query(self):
        return self.url_parse.query

    def get_hmac_signed_headers(self) -> str:
        return ';'.join(self.conf.signer_headers)

    def _static_headers(self) -> dict:
        return {
            'X-HMAC-ALGORITHM': self.get_hash_strategy(),
            'X-HMAC-ACCESS-KEY': self.get_access_key(),
            'X-HMAC-SIGNED-HEADERS': self.get_hmac_signed_headers(),
        }

    def _dynamic_headers(self):
        """动态头:当前时间，自定义头..（签名除外）"""
        dh = dict()
        dh.update(self.extend_headers)
        dh.update(
            {
                'Date': self.date
            }
        )
        return dh

    def _combine_headers(self):
        d = {}
        d.update(self._static_headers())
        d.update(self._dynamic_headers())
        return d

    def _combine_headers_with_signature(self, ):
        headers = self._combine_headers()
        headers.update({'X-HMAC-SIGNATURE': self.get_signer()})
        return headers

    def _build_req_signer_string(self) -> str:
        # 生成待签名字符串

        signer = ''
        ch = self._combine_headers()
        for key in self.conf.signer_headers:
            try:
                value = ch[key]
                signer += f'{key}:{value}\n'
            except KeyError:
                raise RequestError(f'待签名header {key} 未设置')

        return f"""{self.method}\n{self.get_path()}\n{self.get_query()}\n{self.conf.access_key}\n{self.date}\n{signer}"""

    def get_signer(self):
        return hmac_signer(message=bytes(self._build_req_signer_string(), 'utf-8'), conf=self.conf).decode('utf-8')

    def send(self):
        """发送请求"""
        headers = self._combine_headers_with_signature()

        req_url = urljoin(self.conf.gateway_url, self.uri)

        if self.method == "POST":
            if isinstance(self.body, dict):
                r = requests.post(req_url, json=self.body, headers=headers, verify=False)
            else:
                r = requests.post(req_url, data=self.body, headers=headers, verify=False)

        elif self.method == "GET":
            r = requests.get(req_url, headers)

        else:
            raise RequestError(f'no allow http method {self.method}')

        return r.text, r.status_code
