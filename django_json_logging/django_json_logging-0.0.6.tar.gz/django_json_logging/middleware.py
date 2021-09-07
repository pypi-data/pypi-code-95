import base64
import logging
import uuid
from typing import Optional, Callable

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse, QueryDict

from django_json_logging.context import RequestContext

log = logging.getLogger(__name__)


class AccessLogMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        self.log_request(request)
        response: HttpResponse = self.get_response(request)
        self.log_response(response)
        return response

    def log_request(self, request: HttpRequest) -> None:
        RequestContext.set_request_id(self.get_request_id(request))
        RequestContext.set_user(self.get_user(request))
        RequestContext.set_user_session_id(self.get_user_session_id(request))
        RequestContext.set_ip(self.get_ip(request) or self.get_x_forwarded_for(request))
        extra: dict = dict(
            http_method=request.method,
            path=request.path,
            query_params=self.get_query_params(request),
            user_agent=self.get_user_agent(request),
            x_forwarded_for=self.get_x_forwarded_for(request),
        )
        log.info("RX", extra=extra)

    @staticmethod
    def log_response(response: HttpResponse) -> None:
        extra = dict(
            status_code=response.status_code,
            cookies=response.cookies if response.cookies else None,
        )
        log.info("TX", extra=extra)

    @staticmethod
    def get_x_forwarded_for(request: HttpRequest) -> Optional[str]:
        return request.META.get("HTTP_X_FORWARDED_FOR")

    @staticmethod
    def get_ip(request: HttpRequest) -> Optional[str]:
        return request.META.get("REMOTE_ADDR")

    @staticmethod
    def get_user_agent(request: HttpRequest) -> Optional[str]:
        return request.META.get("HTTP_USER_AGENT")

    @staticmethod
    def get_query_params(request: HttpRequest) -> Optional[QueryDict]:
        return request.GET if request.GET else None

    @staticmethod
    def get_user(request: HttpRequest) -> Optional[str]:
        return (
            str(request.user) if not str(request.user) == str(AnonymousUser()) else None
        )

    @staticmethod
    def get_request_id(request: HttpRequest) -> str:
        return request.META.get("HTTP_X_REQUEST_ID") or base64.urlsafe_b64encode(
            uuid.uuid4().bytes
        ).rstrip(b"=").decode("ascii")

    @staticmethod
    def get_user_session_id(request: HttpRequest) -> Optional[str]:
        session = getattr(request, "session", None)
        session_id = getattr(session, "session_key", None)
        return session_id
