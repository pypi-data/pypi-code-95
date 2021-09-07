import json
import logging
import time
from typing import cast, Dict

from _ringding.client import RdClient
from _ringding.messages import Message
from _ringding.ws.wsserver import WebsocketServer

TODO = object


class RdServer:
    def __init__(self, host: str = '127.0.0.1', port: int = 36097,
                 log_level=logging.INFO):
        self._host = host
        self._port = port
        self._log_level = log_level
        self._server: WebsocketServer = cast(WebsocketServer, None)
        self._CLIENTS: Dict[int, RdClient] = {}
        self._entrypoint = None
        self._is_started = False

    def serve(self, entrypoint: object):
        self._server = WebsocketServer(self._port,
                                       host=self._host,
                                       loglevel=self._log_level)
        self._entrypoint = entrypoint
        self._server.set_fn_new_client(self.new_client)
        self._server.set_fn_message_received(self.on_message)
        self._is_started = True
        self._server.run_forever()

    def wait_until_started(self):
        while not self._is_started:
            time.sleep(0.2)
        time.sleep(0.2)  # Give run_forever some time to do what it needs to.

    def stop(self):
        self._is_started = False
        self._server.shutdown()

    def new_client(self, client, server):
        self._CLIENTS[client['id']] = RdClient(server, client, self._entrypoint)

    def on_message(self, client: Dict, server: WebsocketServer, message: str):
        logging.debug(f'Server received message: {message}')
        client = self._CLIENTS.get(client['id'])
        data = Message(**json.loads(message))
        client.on_message(data)
