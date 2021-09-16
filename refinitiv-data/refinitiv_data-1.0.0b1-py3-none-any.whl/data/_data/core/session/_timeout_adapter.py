# coding: utf-8

import time
import types

import requests
import requests_async
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from itertools import takewhile
from math import log2


#################################################################################################
# Override extract_cookies_to_jar from requests lib to fix error within response.headers


def extract_cookies_to_jar(jar, request, response):
    """Extract the cookies from the response into a CookieJar.
    :param jar: cookielib.CookieJar (not necessarily a RequestsCookieJar)
    :param request: our own requests.Request object
    :param response: httpcore.Response object
    """
    msg = HTTPMessage()
    for k, v in response.headers.items():
        msg.add_header(k, v)

    # the _original_response field is the wrapped httplib.HTTPResponse object,
    req = requests.cookies.MockRequest(request)
    # pull out the HTTPMessage with the headers and put it in the mock:
    res = requests.cookies.MockResponse(msg)
    jar.extract_cookies(res, req)


requests_async.cookies.extract_cookies_to_jar.__code__ = extract_cookies_to_jar.__code__


#################################################################################################


class TimeoutRetry(Retry):
    def __init__(self, session=None, timeout: float = None, *args, **kwargs):
        Retry.__init__(self, *args, **kwargs)
        self.consecutive_errors = 0
        self.MAX_RETRIES = log2(timeout) if timeout else self.BACKOFF_MAX
        self.session = session
        self.timeout = timeout
        self.cumulated_backoff_time = 0

    def set_timeout(self, timeout: float = None) -> None:
        self.MAX_RETRIES = log2(timeout) if timeout else self.BACKOFF_MAX
        if timeout:
            self.timeout = timeout

    def get_backoff_time(self) -> float:
        """Formula for computing the current backoff time
        :rtype: float
        """
        # Disable backoff limitation within timeout
        # backoff_time = float(min(self.timeout, super().get_backoff_time()))
        backoff_time = super().get_backoff_time()
        # Disable backoff limitation within timeout
        # if (self.cumulated_backoff_time+backoff_time) > self.timeout:
        #     backoff = self.timeout - self.cumulated_backoff_time
        #     self.session.debug(f"Backoff time {backoff_time} too long regarding timeout, reduce it to {backoff}")
        #     backoff_time = backoff
        self.session.debug(f"Backoff time = {backoff_time}")
        return backoff_time

    def get_previous_backoff_time(self) -> float:
        """Formula for computing the previous backoff time
        :rtype: float
        """
        # We want to consider only the last consecutive errors sequence (Ignore redirects).
        consecutive_errors_len = len(
            list(
                takewhile(lambda x: x.redirect_location is None, reversed(self.history))
            )
        )
        if consecutive_errors_len <= 2:
            return 0

        cumulated_backoff_value = self.backoff_factor * (
            2 ** (consecutive_errors_len - 2)
        )
        self.session.debug(f"Cumulated backoff time = {cumulated_backoff_value}")
        return cumulated_backoff_value

    def increment(self, *args, **kwargs):
        new_retry = super().increment(*args, **kwargs)
        new_retry.cumulated_backoff_time = (
            new_retry.cumulated_backoff_time + new_retry.get_previous_backoff_time()
        )
        self.session.debug(
            f"Number of retries remaining : {self.total} | Cumulated backoff time : {new_retry.cumulated_backoff_time}"
        )
        return new_retry

    def is_exhausted(self) -> bool:
        # Disable custom timeout
        # if self.timeout <= self.cumulated_backoff_time:
        #     self.session.debug(
        #         f"No more retry because timeout ({self.timeout} sec) is reached (cumulated backoff time={self.cumulated_backoff_time})")
        #     return True
        # else:
        return super().is_exhausted()

    def new(self, **kw):
        new_retry = super().new(**kw)
        new_retry.set_timeout(self.timeout)
        new_retry.session = self.session
        new_retry.cumulated_backoff_time = self.cumulated_backoff_time
        return new_retry

    def _sleep_backoff(self):
        backoff = self.get_backoff_time()
        if backoff <= 0:
            return
        # Following code limit the backoff delay within timeout
        # if self.cumulated_backoff_time > self.timeout:
        #     backoff = self.cumulated_backoff_time - self.timeout
        self.session.debug(f"Sleep backoff time({backoff} sec)")
        time.sleep(backoff)


#################################################################################################
#  AsyncHTTPAdapter adds async behaviour to requests.HTTPAdapter,
#  then, it could be used with requests_async.Session

# read function will override requests.HTTPAdapter.Response.read() for compatibility with request_async
async def read(self):
    return self.content


class AsyncHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    # Override HTTPAdapter.send function for compatibility with request_async
    async def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None and hasattr(self, "timeout"):
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)

    # Override HTTPAdapter.build_response function for compatibility with request_async
    def build_response(self, req, resp):
        response = super().build_response(req, resp)
        # Override HTTPAdapter.Response.read function with async read()
        response.read = types.MethodType(read, response)
        return response

    # Override HTTPAdapter.Response.close function for compatibility with request_async
    async def close(self):
        super().close()
