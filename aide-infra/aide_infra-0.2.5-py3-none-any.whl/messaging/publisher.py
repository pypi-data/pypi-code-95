import contextlib
import logging

import pika
from pika.exchange_type import ExchangeType

from aide.messaging.queue_config import RabbitClientConfiguration


logger = logging.getLogger(__name__)


class Publisher():
    def __init__(self, config: RabbitClientConfiguration):
        self.config = config

    @contextlib.contextmanager
    def _channel(self):
        _connection = None
        try:
            credentials = pika.PlainCredentials(username=self.config.username,
                                                password=self.config.password)

            connection_params = pika.ConnectionParameters(host=self.config.host, port=self.config.port,
                                                          credentials=credentials)

            _connection = pika.BlockingConnection(parameters=connection_params)
            logger.info('Connection opened')
            _channel = _connection.channel()
            _channel.exchange_declare(durable=True,
                                      exchange=self.config.exchange,
                                      exchange_type=ExchangeType.direct.value)
            _channel.queue_declare(queue=self.config.queue, durable=True, arguments={"x-queue-type": "quorum"})
            _channel.queue_bind(self.config.queue, self.config.exchange, routing_key=self.config.routing_key)
            yield _channel
        finally:
            if _connection is not None:
                _connection.close()

    def publish_message(self, message, correlation_id=None):
        with self._channel() as channel:
            properties = pika.BasicProperties(content_type='application/json')
            channel.basic_publish(self.config.exchange,
                                  self.config.routing_key,
                                  message,
                                  properties)

            logging.info('Published message. Correlation ID %s', correlation_id)
