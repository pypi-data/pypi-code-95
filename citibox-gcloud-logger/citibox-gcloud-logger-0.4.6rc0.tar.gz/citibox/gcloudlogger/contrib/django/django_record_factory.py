import json
import re

from django.http.request import HttpRequest
from django.http.response import HttpResponse

from citibox.gcloudlogger.src.base_record import Params, Body, RequestHeaders, \
    ResponseHeaders, Response, UserInfo
from citibox.gcloudlogger.src.base_record_factory import BaseLogRecordFactory

BINARY_REGEX = re.compile(r"(.+(Content-Type):.*?)(\S+)/(\S+)(?:\r\n)*(.+)", re.S | re.I | re.IGNORECASE)
BINARY_TYPES = ("image", "application")


class DjangoRecordFactory(BaseLogRecordFactory):
    DJANGO_HEADER_PREFIX = "HTTP_"

    def __init__(
        self,
        logger,
        request: HttpRequest,
        response: HttpResponse,
        view_kwargs: dict,
        request_body,
        created_at=None
    ):
        super().__init__(created_at=created_at)
        self.logger = logger
        self.request = request
        self.request_body = request_body
        self.response = response
        self.view_kwargs = view_kwargs

    def _build_request_headers(self) -> RequestHeaders:
        return RequestHeaders(
            **{k[len(self.DJANGO_HEADER_PREFIX):]: v for k, v in self.request.META.items()} if self.request.META else {}
        )

    def _get_user_info(self) -> UserInfo:
        header = self.request.META.get(f'{self.DJANGO_HEADER_PREFIX}{self.USER_INFO_HEADER}')
        return UserInfo(header) if header else None

    def _build_response_headers(self) -> ResponseHeaders:
        return ResponseHeaders(**dict(self.response.items()))

    def _build_request_params(self) -> Params:
        if self.request.method in ("GET", "DELETE"):
            return Params(
                **{item[0]: item[1] for item in self.request.GET.lists()}
            )

        return Params(**{})

    def _build_request_body(self) -> Body:
        if self.request.method in ("POST", "PUT", "PATCH"):
            content_type = self.request.META.get("CONTENT_TYPE", "")
            if content_type.startswith("multipart/form-data"):  # is form-data, we need to parse it
                return Body(**self._parse_multipart(self.request, content_type))
            else:
                try:
                    if len(self.request.POST) > 0:
                        return Body(**self.request.POST)
                    if len(self.request.body) > 0:
                        return Body(**json.loads(self.request.body))
                except Exception as e:
                    Body(
                        **{"error_message": "Error when parsing request on logger middleware"}
                    )
        return Body(**{})

    def _get_request_uri_path(self) -> str:
        return self.request.path

    def _get_request_view_params(self) -> dict:
        return self.view_kwargs

    def _parse_multipart(self, request: HttpRequest, content_type):
        boundary = "--" + content_type[30:]
        try:
            body = self.request_body.decode()
        except UnicodeDecodeError:
            return {'error': f'(multipart/form) cannot parse form data'}

        parameters = {}

        parts = body.split(boundary)
        for index, part in enumerate(parts):
            match = BINARY_REGEX.search(part)
            if match and match.group(2) in BINARY_TYPES and not match.group(4) in ("", "\r\n"):
                part = match.expand(r"\1\2/\3\r\n\r\n(binary data)\r\n")
            parameters[part] = part

        return parameters

    def _build_response(self, response) -> Response:
        return Response(
            status_code=response.status_code,
            headers=ResponseHeaders(**response.items()),
            body=self._build_response_body(response)
        )

    def _build_response_body(self) -> Body:
        body = Body()

        try:
            if hasattr(self.response, 'data') and self.response.data:
                body = Body(
                    **json.loads(self.response.content)
                )

        except json.JSONDecodeError as e:
            self.logger.warning(f'Error serializing response: {e.msg}')
            body = Body(
                **{"error": f'Error serializing response: {e.msg}'}
            )

        finally:
            return body

    def _build_pubsub_request_attributes(self) -> dict:

        if self.request.META.get('HTTP_USER_AGENT', '').upper() == self.PUBSUB_USER_AGENT.upper():
            message = self.request.POST.get('message', None)

            pubsub_attributes = message.get('attributes', {})
            if not pubsub_attributes:
                self.logger.warning(f'Missing pubsub message attributes on logger middleware')

            return pubsub_attributes

        return dict()

    def _get_host(self) -> str:
        return self.request.get_host()

    def _get_method(self) -> str:
        return self.request.method

    def _get_status_code(self) -> str:
        return self.response.status_code
