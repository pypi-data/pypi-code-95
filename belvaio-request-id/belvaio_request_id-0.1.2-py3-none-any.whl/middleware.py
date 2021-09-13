from typing import Callable

from aiohttp.web import middleware
from aiohttp.web_request import BaseRequest
from aiohttp.web_response import StreamResponse

from belvaio_request_id.utils import get_request_id, reset_request_id, set_request_id

try:
    import sentry_sdk
    from sentry_sdk import configure_scope
except ImportError:  # pragma: nocover
    sentry_sdk = None  # type: ignore


@middleware
async def request_id_middleware(
    request: BaseRequest, handler: Callable
) -> StreamResponse:
    request_id_token = set_request_id(request.headers.get("X-Request-Id"))
    request_id = get_request_id()
    try:
        if sentry_sdk:
            with configure_scope() as scope:
                scope.set_tag("request_id", request_id)
        response = await handler(request)
        if response is not None and hasattr(response, "headers"):
            response.headers["X-Request-Id"] = get_request_id()
        return response
    finally:
        reset_request_id(request_id_token)
