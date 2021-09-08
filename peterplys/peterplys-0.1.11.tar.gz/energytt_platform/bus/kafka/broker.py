from typing import List, Any, Iterable
from functools import cached_property
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

from energytt_platform.bus.broker import MessageBroker, Message
from energytt_platform.bus.serialize import MessageSerializer


class KafkaMessageBroker(MessageBroker):
    """
    Implementation of Kafka as message bus.
    """
    def __init__(self, servers: List[str], serializer: MessageSerializer):
        self.servers = servers
        self.serializer = serializer

    @cached_property
    def _kafka_producer(self) -> KafkaProducer:
        """
        TODO
        """
        return KafkaProducer(
            bootstrap_servers=self.servers,
            value_serializer=self.serializer.serialize,
        )

    def publish(self, topic: str, msg: Any, block=True, timeout=10):
        """
        TODO
        """
        print('PUBLISH: %s' % msg)
        future = self._kafka_producer.send(
            topic=topic,
            value=msg,
        )

        if block:
            try:
                record_metadata = future.get(timeout=timeout)
            except KafkaError as e:
                # Decide what to do if produce request failed...
                raise self.PublishError(str(e))

    def subscribe(self, topics: List[str]) -> Iterable[Message]:
        """
        TODO
        """
        kafka_consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=self.servers,
            value_deserializer=self.serializer.deserialize,
            auto_offset_reset='earliest',
            enable_auto_commit=False,
        )

        return (msg.value for msg in kafka_consumer)

        # return KafkaMessageConsumer(
        #     topics=topics,
        #     servers=self.servers,
        #     serializer=self.serializer,
        # )


# class KafkaMessageConsumer(object):
#     """
#     A kafka_consumer of Kafka messages.
#     Iterates over messages in subscribed topics.
#     """
#
#     def __init__(
#             self,
#             topics: List[str],
#             servers: List[str],
#             serializer: MessageSerializer,
#     ):
#         """
#         :param topics:
#         :param servers:
#         :param serializer:
#         """
#         self.topics = topics
#         self.servers = servers
#         self.serializer = serializer
#
#     @cached_property
#     def kafka_consumer(self) -> KafkaConsumer:
#         """
#         TODO
#         """
#         return KafkaConsumer(
#             *self.topics,
#             bootstrap_servers=self.servers,
#             value_deserializer=self.serializer.deserialize,
#             auto_offset_reset='earliest',
#             enable_auto_commit=False,
#         )
#
#     def __iter__(self):
#         return (msg.value for msg in self.kafka_consumer)
