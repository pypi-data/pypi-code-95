import ssl
from logging import Logger, LoggerAdapter, getLogger
from typing import Optional, Union, Dict, Any
from time import sleep
from pika import BlockingConnection, URLParameters, SSLOptions, BasicProperties
from pika.channel import Channel
from rabbitmq_worker.errors import InvalidChannel


class RabbitmqProducer:
    """
    Main class used to send messages to an exchange.
    """

    def __init__(
        self,
        amqp_url: str,
        ssl_context: Optional[ssl.SSLContext] = None,
        logger: Optional[Union[Logger, LoggerAdapter]] = None,
    ):
        self.amqp_url = amqp_url
        self.ssl_context = ssl_context
        self.logger: Union[Logger, LoggerAdapter] = logger if logger is not None else getLogger(__name__)
        self._connection: Optional[BlockingConnection] = None
        self._channel: Optional[Channel] = None

    def __enter__(self):
        self._connection = self._connect()
        if not self._connection:
            return
        self._channel = self._connection.channel()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self._connection:
            self._connection.close()

    def send_message(self, message: bytes, exchange_name: str, routing_key: str, properties: Dict[str, Any]):
        self._manage_fallback()
        if not self._channel:
            return
        self._channel.basic_publish(exchange_name, routing_key, message, properties=BasicProperties(**properties))
        self.logger.info(
            "message {} sent to exchange {} with routing_key {}".format(message, exchange_name, routing_key)
        )

    def _manage_fallback(self) -> None:
        retry_count = 0
        while self._channel is None or not self._channel.is_open:
            retry_count += 1
            if retry_count >= 5:
                raise InvalidChannel(
                    "After 5 seconds, the channel is still not open. You cannot send a message into a closed channel"
                )
            sleep(1)

    def _connect(self):
        parameters = URLParameters(self.amqp_url)
        if self.ssl_context:
            parameters.ssl_options = SSLOptions(self.ssl_context)
        return BlockingConnection(parameters)
