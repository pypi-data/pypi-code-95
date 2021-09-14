import logging
from typing import Optional

import falcon
import json
from logging import getLogger
from citibox.gcloudlogger.src.base_record import Params, RequestHeaders, Body, ResponseHeaders, UserInfo
from citibox.gcloudlogger.src.base_record_factory import BaseLogRecordFactory

logger = getLogger(__name__)


class FalconRecordFactory(BaseLogRecordFactory):

    def __init__(self, request: falcon.Request, response: falcon.Response, params: dict, created_at=None):
        self.request = request
        self.response = response
        self.params = params
        super().__init__(created_at=created_at)

    def _build_request_params(self) -> Params:
        return Params(**self.request.params)

    def _build_request_body(self) -> Body:
        if self.request.media:
            return Body(**self.request.media)

        return Body()

    def _build_request_headers(self) -> RequestHeaders:
        return RequestHeaders(
            **self.request.headers
        )

    def _get_user_info(self) -> Optional[UserInfo]:
        header = self.request.headers.get(self.USER_INFO_HEADER)
        return UserInfo(header) if header else None

    def _build_response_headers(self) -> ResponseHeaders:
        return ResponseHeaders(**self.response.headers)

    def _build_response_body(self) -> Body:
        if self.response.body:
            return Body(**json.loads(self.response.body))

        return Body()

    def _build_pubsub_request_attributes(self) -> dict:
        if self.request.user_agent.upper() == self.PUBSUB_USER_AGENT.upper():
            return self.request.media['message']['attributes']

        return dict()

    def _get_request_uri_path(self) -> str:
        return self.request.path

    def _get_request_view_params(self) -> dict:
        return self.params

    def _get_host(self) -> str:
        return self.request.host

    def _get_method(self) -> str:
        return self.request.method

    def _get_status_code(self) -> int:
        try:
            status_code = int(self.response.status[:3])
        except Exception:
            status_code = 0
            logger.exception('Status code in falcon middleware could not be processed', extra={
                'original_status_code': self.response.status})
        return status_code
