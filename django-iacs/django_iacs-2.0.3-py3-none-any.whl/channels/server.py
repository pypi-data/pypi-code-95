#!/usr/bin/env python
import os

from channels.routing import get_default_application
from daphne.endpoints import build_endpoint_description_strings
from daphne.server import Server
from django.conf import settings
from ngs.tools.logs import InfoLog, ErrorLog

from ..log import IacsLogger


class WebsocketServer(metaclass=IacsLogger):

    def log_action(self, protocol, action, details):
        # Websocket requests
        if protocol == "websocket":
            if action == "connected":
                self.logger.info(InfoLog("WebSocket CONNECT {path} [{client}]".format(**details)))
            elif action == "disconnected":
                self.logger.info(ErrorLog("WebSocket DISCONNECT {path} [{client}]".format(**details)))
            elif action == "connecting":
                self.logger.info(InfoLog("WebSocket HANDSHAKING {path} [{client}]".format(**details)))
            elif action == "rejected":
                self.logger.info(ErrorLog("WebSocket REJECT {path} [{client}]".format(**details)))

    def daphne(self, port):
        endpoints = build_endpoint_description_strings(host='0.0.0.0', port=port)
        Server(
            application=get_default_application(),
            action_logger=self.log_action,
            endpoints=endpoints,
            server_name='NGS Websocket Server',
            websocket_timeout=-1
        ).run()

    def start(self, port=80):
        os.environ.setdefault('ASGI_THREADS', str(settings.MAX_THREADS))
        self.daphne(port)
