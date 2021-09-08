import abc
import time
from typing import Optional

from citibox.gcloudlogger.src.base_record import BaseRecord, Request, Response, RequestHeaders, ResponseHeaders, Body, \
    Params, UserInfo


class BaseLogRecordFactory(abc.ABC):
    PUBSUB_USER_AGENT = "CloudPubSub-Google"
    USER_INFO_HEADER = 'USER_INFO'

    def __init__(self, created_at=None):
        self.created_at = created_at if created_at else self.get_current_timestamp()

    def build(self) -> BaseRecord:
        return BaseRecord(
            host=self._get_host(),
            method=self._get_method(),
            path=self._get_request_uri_path(),
            url_fingerprint=self._get_url_fingerprint(),
            user_info=self._get_user_info(),
            duration=(self.get_current_timestamp() - self.created_at) / 1000,
            request=Request(
                headers=self._build_request_headers(),
                params=self._build_request_params(),
                body=self._build_request_body(),
            ),
            response=Response(
                status_code=self._get_status_code(),
                headers=self._build_response_headers(),
                body=self._build_response_body()
            ),
            **self._build_pubsub_request_attributes()
        )

    def _get_url_fingerprint(self) -> str:
        fingerprint = self._get_request_uri_path()

        for key, value in self._get_request_view_params().items():
            if value:
                fingerprint = self._get_request_uri_path().replace(value, f'{{{key}}}')

        return fingerprint

    @abc.abstractmethod
    def _get_user_info(self) -> Optional[UserInfo]:
        pass

    @abc.abstractmethod
    def _build_response_body(self) -> Body:
        pass

    @abc.abstractmethod
    def _build_response_headers(self) -> ResponseHeaders:
        pass

    @abc.abstractmethod
    def _build_request_headers(self) -> RequestHeaders:
        pass

    @abc.abstractmethod
    def _build_request_params(self) -> Params:
        pass

    @abc.abstractmethod
    def _build_request_body(self) -> Body:
        pass

    @abc.abstractmethod
    def _build_pubsub_request_attributes(self) -> dict:
        pass

    @abc.abstractmethod
    def _get_request_uri_path(self) -> str:
        pass

    @abc.abstractmethod
    def _get_request_view_params(self) -> dict:
        pass

    @abc.abstractmethod
    def _get_method(self) -> str:
        pass

    @abc.abstractmethod
    def _get_host(self) -> str:
        pass

    @abc.abstractmethod
    def _get_status_code(self) -> str:
        pass

    @staticmethod
    def get_current_timestamp() -> int:
        return int(round(time.time() * 1000))
