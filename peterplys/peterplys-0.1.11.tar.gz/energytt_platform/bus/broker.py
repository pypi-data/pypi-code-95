from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Iterable, Callable, Any

from energytt_platform.serialize import Serializable


@dataclass
class Message(Serializable):
    """
    Base-class for messages that can be sent on the bus.
    Inherited classes must remember to use the @dataclass decorator.
    """
    pass


# Message handler function for consuming
TMessageHandler = Callable[[Message], None]


class MessageBroker(object):
    """
    Abstract base-class for publishing and consuming messages
    on the message-bus.
    """

    class PublishError(Exception):
        """
        TODO
        """
        pass

    class DispatchError(Exception):
        """
        TODO
        """
        pass

    @abstractmethod
    def publish(self, topic: str, msg: Any, block=False, timeout=10):
        """
        Publish a message to a topic on the bus.

        :param topic: The topic to publish to
        :param msg: The message to publish
        :param block: Whether to block until publishing is complete
        :param timeout: Timeout in seconds (if block=True)
        """
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, topics: List[str]) -> Iterable[Message]:
        """
        Subscribe to one or more topics. Returns an iterable of messages.

        :param topics: The topics to subscribe to
        :return: An iterable of messages
        """
        raise NotImplementedError

    def listen(self, topics: List[str], handler: TMessageHandler):
        """
        An alias for subscribe() except this function takes a callable
        which is invoked for each message.

        :param topics: The topics to subscribe to
        :param handler: Message handler
        """
        for msg in self.subscribe(topics):
            handler(msg)
