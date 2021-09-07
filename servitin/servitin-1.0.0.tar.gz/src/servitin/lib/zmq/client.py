import asyncio
import json

import aiozmq.rpc
import zmq
from async_timeout import timeout as atimeout
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from jose import jwt


class ValidationError(Exception):
    pass


class Servitin:
    def __init__(self, service_name, loop=None):
        self.loop = loop
        self.connection = None
        self.algorithm = 'HS256'
        self.service_name = service_name

        sett = f"SERVITIN_{self.service_name.upper()}_ZMQ"
        self.settings = getattr(settings, sett, None)

        if not self.settings:
            raise ImproperlyConfigured(f'{self.service_name} settings.{sett}')

        self.host = self.settings['HOST']
        self.port = self.settings['PORT']
        self.conn_str = f'{self.host}:{self.port}'
        self.secret = self.settings['SECRET']

    async def connect(self, loop=None):
        try:
            if loop:
                self.connection = await aiozmq.rpc.connect_rpc(connect=self.conn_str, loop=loop)
            else:
                self.connection = await aiozmq.rpc.connect_rpc(connect=self.conn_str)
            self.connection.transport.setsockopt(zmq.LINGER, 0)
        except Exception as e:
            raise Exception(f"{self.service_name}: connect error to {self.conn_str}. {e.__repr__()}")

    def close(self):
        self.connection.close()

    async def _request(self, endpoint, data, timeout, loop):
        await self.connect(loop)

        data = {} if not data else data
        data = jwt.encode(data, self.secret, algorithm=self.algorithm)

        with atimeout(timeout):
            resp = await self.connection.call.endpoint(endpoint, data)

        self.close()
        return json.loads(resp)

    def sync_request(self, endpoint, data, timeout=10):

        async def r(svc, loop):
            return await svc._request(endpoint, data, timeout, loop)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            r(self, loop)
        )
        loop.close()

        if response['error'] == 'ValidationError':
            raise ValidationError(response['data'])
        return response

    async def request(self, endpoint, data=None, timeout=10):
        response = await self._request(endpoint, data, timeout, self.loop)
        if response['error'] == 'ValidationError':
            raise ValidationError(response['data'])
        return response
