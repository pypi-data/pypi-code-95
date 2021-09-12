import asyncio
import json
import uuid

import aio_pika
from environs import Env

from .response import Response

env = Env()
env.read_env()  # also reads the .env file in project root

AMQP_URI = env.str('AMQP_URI')


class Producer:
    def __init__(self, loop=None):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.futures = {}
        self.loop = loop or asyncio.get_event_loop()

    async def connect(self):
        self.connection: aio_pika.Connection = await aio_pika.connect_robust(
            AMQP_URI, loop=self.loop
        )
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response, timeout=5)

        return self

    def on_response(self, message: aio_pika.IncomingMessage):
        future = self.futures.pop(message.correlation_id)
        future.set_result(
            Response(
                status=message.headers.get('status'),
                headers=dict(message.headers),
                data=json.loads(message.body)
            )
        )

    async def call(self, routing_key: str, body=None) -> Response:
        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()

        self.futures[correlation_id] = future

        if not body:
            body = {}

        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(body).encode(),
                content_type="application/json",
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=routing_key,
        )
        return await future
