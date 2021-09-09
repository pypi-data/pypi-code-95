import requests
import sys
import logging
import copy
import re
import random


class DefaultLogger(logging.Logger):
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


class MyResponse(object):
    __attrs__ = [
        'meta', 'content', 'status_code', 'headers', 'url', 'history',
        'encoding', 'cookies', 'text', 'check_success', 'exception'
    ]
    failed_code = [500, 502, 503, 504, 508, 597, 407, 408, 400, 403, 429, 404]

    def __init__(self, _resp):
        self.resp = _resp
        self._status_code = None
        self.ok = isinstance(self.resp, requests.models.Response)
        self._exception = None
        self._url = None
        self._meta = {}
        self._text = None
        self._check_success = False

    @property
    def meta(self):
        return self._meta

    @property
    def content(self):
        if self.ok:
            return self.resp.content

    @property
    def status_code(self):
        if self.ok:
            return self.resp.status_code
        else:
            return self._status_code

    @property
    def text(self):
        if self.ok:
            return self.resp.text
        else:
            return self._text

    @property
    def headers(self):
        if self.ok:
            return self.resp.headers

    @property
    def url(self):
        if self.ok:
            return self.resp.url
        else:
            return self._url

    @property
    def cookies(self):
        if self.ok:
            return self.resp.cookies

    @property
    def history(self):
        if self.ok:
            return self.history

    @property
    def check_success(self):
        return self._check_success

    @property
    def exception(self):
        if self._exception is None:
            return self._exception
        exc_type, exc_value, _ = self._exception
        exc_type = str(exc_type).replace("'", "").replace(">", "").replace("<", "").replace("class ", "")
        return {"exc_type": exc_type,
                "exc_value": str(exc_value)}


class Downloader(object):

    @classmethod
    def get(cls, **kwargs):
        return cls._retry_request(method="get", **kwargs)

    @classmethod
    def post(cls, **kwargs):
        return cls._retry_request(method="post", **kwargs)

    @classmethod
    def _retry_request(cls, **kwargs):
        retry_times = kwargs.pop("retry_times", 10)
        assert isinstance(retry_times, int) and retry_times >= 1
        success_code = kwargs.pop("success_code", [200])
        success_code = [success_code] if not isinstance(success_code, list) else success_code
        customize_check_func = kwargs.pop("check_func", None)
        logger = kwargs.pop("logger", DefaultLogger)
        assert issubclass(logging.Logger, logging.Logger)
        resp = None
        meta = kwargs.pop("meta", {})
        while retry_times > 0:
            kwargs["proxies"] = cls.lum_rand_session(kwargs.get("proxies"))
            logger.debug("\nretry_times:{} ,\nkwargs:{}".format(retry_times, kwargs))
            resp = cls._request(**copy.deepcopy(kwargs))
            resp._meta = meta
            logger.debug("\nresponse status_code:{}\n".format(resp.status_code))
            if resp.ok:
                if not hasattr(customize_check_func, "__call__"):
                    if cls.default_check_func(resp=resp, success_code=success_code):
                        resp._check_success = True
                        return resp
                else:
                    if customize_check_func(resp):
                        resp._check_success = True
                        return resp
            retry_times -= 1
        return resp

    @staticmethod
    def _request(**kwargs):
        try:
            resp = requests.request(**kwargs)
            resp = MyResponse(resp)
            return resp
        except Exception as resp_exception:
            resp = MyResponse(resp_exception)
            resp._status_code = -1
            resp._url = kwargs.get("url") or ""
            resp._text = None
            resp._exception = sys.exc_info()
            return resp

    @staticmethod
    def default_check_func(resp, success_code):
        if resp.status_code in success_code:
            return True

    @staticmethod
    def lum_rand_session(proxies):
        if proxies is None:
            return proxies
        session_id = re.findall(r"session-(.*?):", proxies.get("https"))
        session_id = session_id[0] if session_id else "replace_pass"
        _proxy = proxies.get("https").replace(session_id, str(random.randint(1, 10000000)))
        return {"https": _proxy, "http": _proxy}


if __name__ == '__main__':
    pass
