# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import contrast
from contrast.agent import scope as contrast_scope
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from contrast.agent.middlewares.base_middleware import BaseMiddleware
from contrast.agent.middlewares.response_wrappers.fastapi_response_wrapper import (
    FastApiResponseWrapper,
)
from contrast.agent.middlewares.route_coverage.fastapi_routes import (
    create_fastapi_routes,
    build_fastapi_route,
)
from contrast.agent.request_context import RequestContext
from contrast.agent.asgi import scope_to_environ
from contrast.extern import structlog as logging
from contrast.extern.six import ensure_binary, iteritems
from contrast.utils.exceptions.security_exception import SecurityException
from contrast.utils.decorators import fail_safely, log_time_cm
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)


logger = logging.getLogger("contrast")


class FastApiMiddleware(BaseMiddleware, BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, original_app: FastAPI) -> None:
        self.app = app
        self.original_app = original_app
        self.app_name = self.original_app.title

        self.dispatch_func = self.agent_dispatch_func
        super(FastApiMiddleware, self).__init__()

    async def agent_dispatch_func(self, request: Request, call_next):
        """
        Instead of implementing a __call__ function, we rely on
        BaseHTTPMiddleware's __call__ func which calls self.dispatch_func.
        """
        if self.is_agent_enabled():
            context = RequestContext(scope_to_environ(request.scope))
            with contrast.CS__CONTEXT_TRACKER.lifespan(context):
                return await self.call_with_agent(context, request, call_next)

        return await self.call_without_agent_async(request, call_next)

    async def call_without_agent_async(self, request: Request, call_next):
        super(FastApiMiddleware, self).call_without_agent()
        return await call_next(request)

    async def call_with_agent(self, context, request: Request, call_next):
        scope = request.scope

        self.log_start_request_analysis(scope.get("path"))
        # TODO: PYT-1717
        # track_environ_sources("wsgi", context, environ)
        try:
            self.prefilter(context)

            with log_time_cm("app code and get response"):
                response = await self.call_next(request)

            with contrast_scope.contrast_scope():
                wrapped_response = FastApiResponseWrapper(response)

            await self.extract_response_to_context_async(wrapped_response, context)

            self.postfilter(context)
            self.check_for_blocked(context)
            return response

        except ContrastServiceException as e:
            logger.warning(e)
            return await self.call_without_agent_async(request, call_next)
        except Exception as e:
            response = self.handle_exception(e)
            return response
        finally:
            self.handle_ensure(context, context.request)
            self.log_end_request_analysis(context.request.path)
            # TODO: PYT-1717 uncomment when assess is enabled
            # if self.settings.is_assess_enabled():
            #     contrast.STRING_TRACKER.ageoff()

    @fail_safely("Unable to get route coverage", return_value={})
    def get_route_coverage(self):
        return create_fastapi_routes(self.original_app)

    @fail_safely("Unable to get FastAPI view func")
    def get_view_func(self, request):
        path = request.path
        if not path:
            return None

        # Checking for `==` works here because fastapi correctly re-routes
        # if user adds (or doesn't) a /. So this method may be called
        # multiple times per request.
        matching_routes = [x for x in self.original_app.routes if x.path == path]

        if not matching_routes:
            return None

        view_func = matching_routes[0].endpoint
        return view_func

    @fail_safely("Unable to build route", return_value="")
    def build_route(self, view_func, url):
        return build_fastapi_route(url, view_func)

    def generate_security_exception_response(self):
        return PlainTextResponse(self.OVERRIDE_MESSAGE, SecurityException.STATUS_CODE)

    async def extract_response_to_context_async(self, response, context):
        """
        Async method to extract response information.
        Unlike the similarly named method in RequestContext, we define
        this method here because defining any async method in RequestContext
        causes SyntaxError for Py2. We can move this once we deprecate Py2.
        """
        context.response = response

        if not self.settings.response_scanning_enabled:
            return

        context.activity.http_response.response_code = response.status_code

        for key, values in iteritems(response.headers.dict_of_lists()):
            normalized_key = key.upper().replace("-", "_")
            response_headers = (
                context.activity.http_response.normalized_response_headers
            )
            response_headers[normalized_key].key = key
            response_headers[normalized_key].values.extend(values)

        body = await response.body

        context.activity.http_response.response_body_binary = ensure_binary(body or "")
