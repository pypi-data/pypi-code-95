import logging

from aiohttp.web_log import AccessLogger
from aiohttp.web_request import BaseRequest
from aiohttp.web_response import StreamResponse

from belvaio_request_id.utils import get_request_id, reset_request_id, set_request_id


class RequestIdAccessLogger(AccessLogger):
    """
    Since aiohttp request access log message is logged outside the scope
    where we set the context var, we need to define our own AccessLogger
    that fixes this.
    """

    def log(self, request: BaseRequest, response: StreamResponse, time: float):
        token = set_request_id(response.headers.get("X-Request-Id"))
        try:
            super().log(request, response, time)
        finally:
            reset_request_id(token)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.__dict__.update({"request_id": get_request_id()})
        return True
