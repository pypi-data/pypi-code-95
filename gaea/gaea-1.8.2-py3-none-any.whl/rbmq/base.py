import pika

from gaea.config import CONFIG
from gaea.errors import AlreadyInitialized
from gaea.log import logger

RBMQ_DEFAULT_EXCHANGE = "akingbee.main_exchange"
RBMQ_DEAD_LETTER_EXCHANGE = "akingbee.dead_letter"


class RBMQClient:
    def __init__(
        self, exchange=None, connection_manager=None, dead_letter_exchange=None
    ):
        self.connection_manager = connection_manager or RBMQConnectionManager()
        self.exchange = exchange or RBMQ_DEFAULT_EXCHANGE
        self.dead_letter_exchange = dead_letter_exchange or RBMQ_DEAD_LETTER_EXCHANGE

        with self.connection_manager as channel:
            self.declare_exchange(channel=channel)

    def declare_exchange(self, channel):
        channel.exchange_declare(
            exchange=self.exchange,
            exchange_type="topic",
            durable=True,
        )
        channel.exchange_declare(
            exchange=RBMQ_DEAD_LETTER_EXCHANGE,
            exchange_type="topic",
            durable=True,
        )

    def close(self):
        self.connection_manager.close()


class RBMQConnectionManager:
    def __init__(self):
        self.connection = self._get_connection()
        self._channel = None

    def __enter__(self):
        if self._channel is not None:
            raise AlreadyInitialized("A rabbitmq channel is already in use")
        self._channel = self.get_channel()
        return self._channel

    def __exit__(self, tp, vl, tb):
        self._clear_channel()

    def get_channel(self):
        return self.connection.channel()

    def _clear_channel(self):
        if self._channel:
            self._channel.close()
            self._channel = None

    def close(self):
        self._clear_channel()
        self.connection.close()

    def _get_connection(self):
        params = self._get_connection_parameters()
        return pika.BlockingConnection(parameters=params)

    @staticmethod
    def _get_connection_parameters():
        creds = pika.PlainCredentials(CONFIG.RBMQ_USER, CONFIG.RBMQ_PASSWORD)
        return pika.ConnectionParameters(
            host=CONFIG.RBMQ_HOST,
            port=CONFIG.RBMQ_PORT,
            virtual_host=CONFIG.RBMQ_VHOST,
            credentials=creds,
            blocked_connection_timeout=300,
        )
