from functools import partial
from logging import Logger, LoggerAdapter, getLogger
import threading
import ssl
from time import sleep
from typing import Callable, Optional, Union, List
from pika import SelectConnection, URLParameters, SSLOptions
from pika.channel import Channel


class InternalConsumer:
    def __init__(
        self,
        amqp_url: str,
        callback: Callable,
        queue_name: str,
        auto_ack: bool,
        ssl_context: Optional[ssl.SSLContext],
        logger: Union[Logger, LoggerAdapter],
    ):
        self.amqp_url: str = amqp_url
        self.callback: Callable = callback
        self.should_reconnect: bool = False
        self.queue_name: str = queue_name
        self.auto_ack: bool = auto_ack
        self.was_consuming: bool = False
        self.ssl_context: Optional[ssl.SSLContext] = ssl_context
        self.logger: Union[Logger, LoggerAdapter] = logger
        self.threads: List[threading.Thread] = []
        self.has_started: bool = False
        self._connection: Optional[SelectConnection] = None
        self._channel: Optional[Channel] = None

        self._closing: bool = False
        self._consuming: bool = False
        self._consumer_tag: Optional[str] = None

    def run(self) -> None:
        self._connection = self._connect()
        self._connection.ioloop.start()

    def stop(self) -> None:
        if not self._closing:
            self._closing = True
            self.logger.info("Stopping")
            if self._connection:
                if self._consuming:
                    self._stop_consuming()
                    self._connection.ioloop.start()
                else:
                    self._connection.ioloop.stop()
            self.logger.info("Stopped")

    def _stop_consuming(self):
        if self._channel and self._consumer_tag:
            callback = partial(self._on_cancelok, userdata=self._consumer_tag)
            self._channel.basic_cancel(self._consumer_tag, callback)

    def _on_cancelok(self, _unused_frame, userdata):
        self._consuming = False
        self.logger.info("RabbitMQ acknowledged the cancellation of the consumer: {}".format(userdata))
        self._channel.close()

    def _connect(self) -> SelectConnection:
        parameters = URLParameters(self.amqp_url)
        if self.ssl_context:
            parameters.ssl_options = SSLOptions(self.ssl_context)
        return SelectConnection(
            parameters=parameters,
            on_open_callback=self._on_connection_open,
            on_open_error_callback=self._on_connection_open_error,
            on_close_callback=self._on_connection_closed,
        )

    def _on_connection_open(self, _connection: SelectConnection) -> None:
        self._open_channel()

    def _open_channel(self) -> None:
        if self._connection:
            self._connection.channel(on_open_callback=self._on_channel_open)

    def _on_channel_open(self, channel: Channel):
        self._channel = channel
        self._channel.add_on_close_callback(self._on_channel_closed)
        self._set_qos()

    def _on_channel_closed(self, channel: Channel, reason: str):
        self.logger.info("Channel {} was closed for reason {}".format(channel.channel_number, reason))
        self._close_connection()

    def _close_connection(self):
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            self.logger.info("Connection already closed")
        else:
            self.logger.info("Closing the connection")
            self._connection.close()

    def _set_qos(self):
        self._channel.basic_qos(prefetch_count=1, callback=self._on_basic_qos_ok)

    def _on_basic_qos_ok(self, _frame):
        self._start_consuming()

    def _start_consuming(self):
        self.has_started = True
        self._add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(
            self.queue_name, on_message_callback=self._on_message, auto_ack=self.auto_ack
        )
        self.was_consuming = True
        self._consuming = True

    def _add_on_cancel_callback(self):
        self._channel.add_on_cancel_callback(self._on_consumer_cancelled)

    def _on_consumer_cancelled(self, method_frame):
        self.logger.info("Consumer was cancelled , shutting down {}".format(method_frame))
        if self._channel:
            self._channel.close()

    def _on_message(self, channel: Channel, basic_deliver, properties, body: bytes):
        thread = threading.Thread(target=self.callback, args=(channel, basic_deliver, properties, body))
        thread.start()
        self.threads.append(thread)

    def _on_connection_open_error(self, _connection, err):
        self.logger.info("Error during open connection: {}. Err: {}".format(_connection, err))
        self._reconnect()

    def _on_connection_closed(self, _connection, reason):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self.logger.info("Connection closed, reconnect for reason {}".format(reason))
            self._reconnect()

    def _reconnect(self):
        self.should_reconnect = True
        self.stop()


class RabbitmqWorker:
    """
    Main worker used to consume messages from a queue
    :param amqp_url: the rabbitmq url used to by the worker to connect.
    :param queue_name: The queue name where to consume messages.
    :param callback: The function used as soon as a message has been consumed.
    :param reconnect_delay: The number of seconds between each reconnection to rabbitmq.
    :param auto_ack: If true, all messages will be acknowledged before being processed.
    :param ssl_context: SSLContext used if you need a TLS connection to rabbitmq.
    :param logger: Custom logger if required.
    """

    def __init__(
        self,
        amqp_url: str,
        queue_name: str,
        callback: Callable,
        reconnect_delay: int = 1,
        auto_ack: bool = False,
        ssl_context: Optional[ssl.SSLContext] = None,
        logger: Optional[Union[Logger, LoggerAdapter]] = None,
        max_retries: int = 3,
    ):
        self.amqp_url: str = amqp_url
        self.queue_name: str = queue_name
        self.callback: Callable = callback
        self.reconnect_delay: int = self._validate_reconnect_delay(reconnect_delay)
        self.auto_ack: bool = auto_ack
        self.ssl_context: Optional[ssl.SSLContext] = ssl_context
        self.logger: Union[Logger, LoggerAdapter] = logger if logger is not None else getLogger(__name__)
        self._is_running: bool = True
        self._max_retries: int = max_retries
        self._current_number_of_retry: int = 0
        self._consumer: InternalConsumer = InternalConsumer(
            self.amqp_url, self.callback, self.queue_name, self.auto_ack, self.ssl_context, self.logger
        )

    def run(self):
        while self._is_running:
            self._current_number_of_retry += 1
            if self._current_number_of_retry > self._max_retries:
                raise Exception("Impossible to connect to rabbitmq with url {} after 3 retries".format(self.amqp_url))
            try:
                self._consumer.run()
            except KeyboardInterrupt:
                self._consumer.stop()
                break
            self._should_reconnect()

        for thread in self._consumer.threads:
            if thread.is_alive():
                thread.join()

    def _should_reconnect(self):
        if self._consumer.should_reconnect:
            if self._consumer.has_started:
                self._current_number_of_retry = 0
            self._consumer.stop()
            sleep(self._get_reconnect_delay())
            self._consumer = InternalConsumer(
                self.amqp_url, self.callback, self.queue_name, self.auto_ack, self.ssl_context, self.logger
            )

    def _get_reconnect_delay(self):
        if self._consumer.was_consuming:
            self.reconnect_delay = 0
        else:
            self.reconnect_delay += 1
        if self.reconnect_delay > 30:
            self.reconnect_delay = 30

        return self.reconnect_delay

    def _validate_reconnect_delay(self, reconnect_delay: int) -> int:
        if reconnect_delay <= 0 or reconnect_delay > 30:
            raise ValueError("Reconnect delay value must be between 1 and 30 seconds")

        return reconnect_delay
