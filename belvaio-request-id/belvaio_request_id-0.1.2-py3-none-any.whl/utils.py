import logging
from contextvars import ContextVar, Token
from typing import Optional
from uuid import UUID, uuid4

from aiohttp.web_log import AccessLogger

logger = logging.getLogger(__name__)

_request_id_ctx_var: ContextVar[str] = ContextVar("belvo_request_id", default="")


def set_request_id(request_id: Optional[str] = None) -> Token:
    if request_id:
        try:
            UUID(request_id)
        except (ValueError, AttributeError):
            logger.exception("Received invalid request id. Using a new one.")
            request_id = None

    request_id = request_id or uuid4().hex
    return _request_id_ctx_var.set(request_id)


def get_request_id() -> str:
    return _request_id_ctx_var.get()


def reset_request_id(request_id: Token):
    _request_id_ctx_var.reset(request_id)
