import logging

import pika
from pika.exchange_type import ExchangeType

from aide.messaging.queue_config import QueueConfiguration


class Publisher():
    def __init__(self, config: QueueConfiguration):
        self.config = config

    def _connect(self):
        credentials = pika.PlainCredentials(username=self.config.username,
                                            password=self.config.password)

        connection_params = pika.ConnectionParameters(
            host=self.config.host,
            port=self.config.port,
            credentials=credentials)

        self._connection = pika.BlockingConnection(parameters=connection_params)
        logging.info('Connection opened')
        self._channel = self._connection.channel()
        # self._channel.add_on_close_callback(self._on_channel_closed)
        self._channel.exchange_declare(
            durable=True,
            exchange=self.config.model_exchange,
            exchange_type=ExchangeType.direct)
        self._channel.queue_declare(queue=self.config.queue, durable=True,
                                    arguments={"x-queue-type": "quorum"})
        self._channel.queue_bind(
            self.config.queue,
            self.config.model_exchange,
            routing_key=self.config.model_routing_key)

    def publish_message(self, message):
        # @todo this is not yet ready
        self._channel.basic_publish(message, None, None)
