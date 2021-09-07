from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

_request_id = ContextVar("_request_id", default=None)
_user = ContextVar("_user", default=None)
_us_id = ContextVar("_us_id", default=None)
_ip = ContextVar("_ip", default=None)


@dataclass
class RequestContext:
    @classmethod
    def set_request_id(cls, val: Any) -> None:
        _request_id.set(val)

    @classmethod
    def set_user(cls, val: Any) -> None:
        _user.set(val)

    @classmethod
    def set_user_session_id(cls, val: Any) -> None:
        _us_id.set(val)

    @classmethod
    def set_ip(cls, val: Any) -> None:
        _ip.set(val)

    @classmethod
    def get_request_id(cls) -> Any:
        return _request_id.get()

    @classmethod
    def get_user(cls) -> Any:
        return _user.get()

    @classmethod
    def get_user_session_id(cls) -> Any:
        return _us_id.get()

    @classmethod
    def get_ip(cls) -> Any:
        return _ip.get()

    @classmethod
    def to_dict(cls) -> dict:
        return dict(
            request_id=_request_id.get(),
            user=_user.get(),
            user_session_id=_us_id.get(),
            ip=_ip.get(),
        )
