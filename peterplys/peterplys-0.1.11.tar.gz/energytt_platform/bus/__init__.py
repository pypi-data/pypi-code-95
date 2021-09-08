from typing import List

from .registry import MessageRegistry
from .kafka import KafkaMessageBroker
from .serialize import MessageSerializer
from .dispatcher import MessageDispatcher
from .broker import MessageBroker, Message


message_registry = MessageRegistry()


def get_default_broker(servers: List[str]) -> MessageBroker:
    """
    Creates and returns an instance of the default message broker.

    :param servers: List of broker servers in the format "IP:PORT"
    :return: An instance of the default message broker
    """
    return KafkaMessageBroker(
        servers=servers,
        serializer=MessageSerializer(registry=message_registry),
    )
