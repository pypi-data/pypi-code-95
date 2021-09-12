import abc
import inspect
import json
import logging
from functools import partial

import aio_pika
import marshmallow
from aio_pika import Exchange, IncomingMessage, Message, types

from .http_status import HTTPStatus
from .response import Response

logger = logging.getLogger(__name__)

ACTION_DATA_KEY = '__action_data__'


def action(
        basename: str = None,
        durable: bool = False,
        exclusive: bool = False,
        timeout: types.TimeoutType = None,
        auto_delete: bool = False,
        arguments: dict = None,
        passive=False,
):
    if arguments is None:
        arguments = {}

    def decorator(func: callable):
        async def wrapper(consumer: AbstractConsumer, exchange: Exchange, message: IncomingMessage):
            try:
                return await func(consumer, exchange, message)
            except marshmallow.exceptions.ValidationError as err:
                logger.exception(
                    'Fail while processing incoming request #{0}'.format(
                        message.message_id))
                return await consumer.publish(exchange, message, Response.from_exc(
                    status=HTTPStatus.BAD_REQUEST,
                    exc=err,
                    data={
                        **err.normalized_messages()
                    }
                ))
            except Exception as err:
                logger.exception(
                    'Unable to process incoming request #{0}'.format(
                        message.message_id))
                return await consumer.publish(exchange, message, Response.from_exc(
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                    exc=err,
                ))

        # TODO: x-dead-letter-exchange
        setattr(wrapper, ACTION_DATA_KEY, {
            'basename': basename or func.__name__,
            'durable': durable,
            'exclusive': exclusive,
            'timeout': timeout,
            'auto_delete': auto_delete,
            'arguments': arguments,
            'passive': passive,
        })
        return wrapper

    return decorator


class AbstractConsumer(abc.ABC):
    DEFAULT_ACTIONS = {
        'create',
        'retrieve',
        'list',
        'partial_update',
        'destroy',
    }

    consumer_key: str
    channel_number: int = 1
    prefetch_count: int = 100

    def __init__(self, connection: aio_pika.Connection):
        self.connection = connection
        self.channel = self.connection.channel(channel_number=self.channel_number)

    async def _create_queue(self, basename, **kwargs) -> aio_pika.Queue:
        """
        :param basename: the base to use for the queue name that are created.
        :return: created queue
        """
        return await self.channel.declare_queue(
            name=':'.join([self.consumer_key, basename]),
            **kwargs
        )

    async def initialize(self):
        """Initialize channel, queue and consumers."""
        await self.channel.initialize()
        await self.channel.set_qos(self.prefetch_count)

        consumers = []
        data: dict
        for name, method_ref in inspect.getmembers(self, predicate=inspect.ismethod):
            if data := getattr(method_ref, ACTION_DATA_KEY, None):
                queue = await self._create_queue(**data)

                # Start listening the queue
                await queue.consume(partial(
                    method_ref, self.channel.default_exchange)
                )
                consumers.append(queue)

        logger.debug('Registered {0} consumers of {1}: {2}'.format(
            len(consumers),
            self.__class__.__name__,
            consumers,
        ))

    @staticmethod
    async def publish(exchange: Exchange, message: IncomingMessage, response: Response):
        await exchange.publish(
            Message(
                headers=response.headers,
                body=json.dumps(response.data).encode(),
                content_type='application/json',
                correlation_id=message.correlation_id,
            ),
            routing_key=message.reply_to,
        )
