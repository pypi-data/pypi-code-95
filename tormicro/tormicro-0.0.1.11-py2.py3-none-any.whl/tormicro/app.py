# Copyright (c) 2020. All rights reserved.

import logging
import re
import traceback
import uuid
from abc import ABC
from types import TracebackType
from typing import (
    Any,
    Awaitable,
    Dict,
    Optional,
    Type, )

import tornado.web

import tormicro.utils.logutils as logutils
from tormicro.config import ConfigDict
from tormicro.doc import setup_swagger
from tormicro.rest import RestHandler


class BaseRequestHandler(tornado.web.RequestHandler):
    def initialize(
            self,
            config: Dict,
            logger: logging.Logger
    ) -> None:
        self.config = config
        self.logger = logger

    def prepare(self) -> Optional[Awaitable[None]]:
        req_id = uuid.uuid4().hex
        logutils.set_log_context(
            req_id=req_id,
            method=self.request.method,
            uri=self.request.uri,
            ip=self.request.remote_ip
        )

        logutils.log(
            self.logger,
            logging.DEBUG,
            include_context=True,
            message='REQUEST'
        )

        return super().prepare()

    def on_finish(self) -> None:
        super().on_finish()

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        body = {
            'method': self.request.method,
            'uri': self.request.path,
            'code': status_code,
            'message': self._reason
        }

        logutils.set_log_context(reason=self._reason)

        if 'exc_info' in kwargs:
            exc_info = kwargs['exc_info']
            logutils.set_log_context(exc_info=exc_info)
            if self.settings.get('serve_traceback'):
                # in debug mode, send a traceback
                trace = '\n'.join(traceback.format_exception(*exc_info))
                body['trace'] = trace

        self.finish(body)

    def log_exception(
            self,
            typ: Optional[Type[BaseException]],
            value: Optional[BaseException],
            tb: Optional[TracebackType],
    ) -> None:
        # https://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler.log_exception
        if isinstance(value, tornado.web.HTTPError):
            if value.log_message:
                msg = value.log_message % value.args
                logutils.log(
                    tornado.log.gen_log,
                    logging.WARNING,
                    status=value.status_code,
                    request_summary=self._request_summary(),
                    message=msg
                )
        else:
            logutils.log(
                tornado.log.app_log,
                logging.ERROR,
                message='Uncaught exception',
                request_summary=self._request_summary(),
                request=repr(self.request),
                exc_info=(typ, value, tb)
            )


class DefaultRequestHandler(BaseRequestHandler):
    def initialize(  # type: ignore
            self,
            status_code: int,
            message: str,
            logger: logging.Logger
    ):
        self.logger = logger
        self.set_status(status_code, reason=message)

    def prepare(self) -> Optional[Awaitable[None]]:
        raise tornado.web.HTTPError(
            self._status_code,
            'request uri: %s',
            self.request.uri,
            reason=self._reason
        )


class BaseRestHandler(RestHandler, BaseRequestHandler):
    pass


class IndexRequestHandler(BaseRequestHandler, ABC):
    URI_PATTERN = r'/?'

    async def get(self):
        """
        ---
        tags:
        - Hello
        summary: echo entry
        description: echo entry to reply hello
        produces:
        - text/plain
        responses:
          200:
            description: hello from the tormicro app

        """
        echo = f'hello from {self.config.application.name}'

        self.set_status(200)
        await self.finish(echo)


class InfoRequestHandler(BaseRequestHandler, ABC):
    URI_PATTERN = r'/actuator/info'

    async def get(self):
        """
        ---
        tags:
        - Actuator
        summary: the actuator info entry
        description: reply an info dict of the tormicro app
        produces:
        - application/json
        responses:
          200:
            description: info dict of the tormicro app
            schema:
              type: object
              properties:
                name:
                  type: string
                  example: app-tormicro
                port:
                  type: integer
                  example: 8080
                ip:
                  type: string
                  example: 127.0.0.1
        """

        def get_local_ip() -> str:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip

        info_dict = dict(
            name=self.config.application.name,
            version=self.config.application.version,
            port=self.config.server.port,
            ip=get_local_ip()
        )

        self.set_status(200)
        await self.finish(info_dict)


def log_function(handler: tornado.web.RequestHandler) -> None:
    # https://www.tornadoweb.org/en/stable/web.html#tornado.web.Application.settings

    logger = getattr(handler, 'logger', logging.getLogger('tormicro'))

    if handler.get_status() < 400:
        level = logging.INFO
    elif handler.get_status() < 500:
        level = logging.WARNING
    else:
        level = logging.ERROR

    logutils.log(
        logger,
        level,
        include_context=True,
        message='RESPONSE',
        status=handler.get_status(),
        time_ms=(1000.0 * handler.request.request_time())
    )

    logutils.clear_log_context()


def make_tormicro_app(
        config: ConfigDict,
        debug: bool,
        logger: logging.Logger,
        rest_mode: bool = True
) -> tornado.web.Application:
    
    app_name = config.application.name
    app_description = config.application.description
    app_version = config.application.version
    
    from tormicro.utils import modutils
    handler_classes = modutils.iter_classes(BaseRequestHandler, 'handlers',
                                            class_filter=lambda h: not issubclass(h, BaseRestHandler))

    handlers = [
        tornado.web.url(IndexRequestHandler.URI_PATTERN, IndexRequestHandler, dict(config=config, logger=logger)),
        tornado.web.url(InfoRequestHandler.URI_PATTERN, InfoRequestHandler, dict(config=config, logger=logger)),
    ]
    for handler_class in handler_classes:
        handlers.append(tornado.web.url(handler_class.URI_PATTERN, handler_class, dict(config=config, logger=logger)))

    if rest_mode:
        def _generateRestServices(rest):
            svs = []
            paths = rest.get_paths()
            for p in paths:
                s = re.sub(r'(?<={)\w+}', '.*', p).replace('{', '')
                o = re.sub(r'(?<=<)\w+', '', s).replace('<', '').replace('>', '').replace('&', '').replace('?', '')
                svs.append(tornado.web.url(o, rest, dict(config=config, logger=logger)))

            return svs

        rest_handler_classes = modutils.iter_classes(BaseRestHandler, 'handlers')

        rest_services = []
        for r in rest_handler_classes:
            svs = _generateRestServices(r)
            rest_services += svs
        if rest_services:
            handlers += rest_services

    logutils.log(logger, logging.INFO,
                 message=f'Setup swagger api-doc for app {app_name}, version={app_version}')
    setup_swagger(handlers, app_name=app_name, app_description=app_description, app_version=app_version)
    
    app = tornado.web.Application(
        [
            # Address Book endpoints
            *handlers
        ],
        compress_response=True,  # compress textual responses
        log_function=log_function,  # log_request() uses it to log results
        serve_traceback=debug,  # it is passed on as setting to write_error()
        default_handler_class=DefaultRequestHandler,
        default_handler_args={
            'status_code': 404,
            'message': 'Unknown Endpoint',
            'logger': logger
        }
    )

    return app
