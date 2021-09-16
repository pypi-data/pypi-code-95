# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from starlette.concurrency import iterate_in_threadpool
from contrast.extern.webob.headers import ResponseHeaders
from contrast.agent.middlewares.response_wrappers.base_response_wrapper import (
    BaseResponseWrapper,
)


class FastApiResponseWrapper(BaseResponseWrapper):
    def __init__(self, response):
        self._response = response
        self._streaming_cache = None

    @property
    async def body(self):
        return await self._get_streaming_content()

    @property
    def headers(self):
        return ResponseHeaders(self._response.headers)

    @property
    def status_code(self):
        return self._response.status_code

    async def _get_streaming_content(self):
        """
        Safely extract the content of a streaming response body. This method guarantees that the
        response body is restored after extraction. Unfortunately, this is likely a performance hit
        to applications streaming large response bodies.

        :return: body of a streaming response as bytes
        """
        if not self._streaming_cache:
            # body_iterator is a AsyncGenerator
            chunks = [chunk async for chunk in self._response.body_iterator]
            body = b"".join(chunks)
            # The original body_iterator is defined in
            # starlette/middleware/base.py:BaseHTTPMiddleware:call_next:body_stream
            # Which is then passed on to StreamingResponse. The latter calls
            # iterate_in_threadpool, too, so we use that same idea here.
            self._response.body_iterator = iterate_in_threadpool(iter(chunks))
            self._streaming_cache = body
            return self._streaming_cache

        return self._streaming_cache
