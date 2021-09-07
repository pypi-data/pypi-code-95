import itertools
import json
from time import sleep

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroProducer, loads
from fastavro.validation import validate


class KafkaToolbox:
    """
    Helpful functions for manipulating Kafka.
    """

    def __init__(self, config):
        self.config = config
        self.admin_client = AdminClient(self.config)

    def create_topic(self, topic, num_partitions, replication_factor):
        topics = [NewTopic(topic=topic, num_partitions=num_partitions, replication_factor=replication_factor)]
        futures = self.admin_client.create_topics(topics)
        _wait_on_futures_map(futures)

    def delete_topic(self, topic):
        futures = self.admin_client.delete_topics(list(topic))
        _wait_on_futures_map(futures)

    def list_topics(self):
        return list(self.admin_client.list_topics().topics)

    def produce_message(self, topic, message, schema, schema_registry_url):
        validate(message, schema)
        producer = AvroProducer(
            {
                **self.config,
                "schema.registry.url": schema_registry_url,
            },
            default_key_schema=loads(json.dumps({"type": "string"})),
            default_value_schema=loads(json.dumps(schema)),
        )
        # TODO pass on_delivery callback function to handle errors
        producer.produce(topic=topic, key="timestamp", value=message)
        producer.flush()

    def wipe_topic(self, topic):
        topics = self.admin_client.list_topics().topics
        topic_to_recreate = topics[topic]
        partitions = topic_to_recreate.partitions.values()
        replicas = set(itertools.chain.from_iterable(p.replicas for p in partitions))
        self.admin_client.delete_topic(topic)
        while True:
            try:
                # until KIP-516 is implemented, success of topic creation seems
                # to be the only way to detect topic deletion is finished.
                self.admin_client.create_topics(topic, num_partitions=len(partitions), replication_factor=len(replicas))
                break
            except:  # pylint: disable=bare-except
                sleep(0.1)


def _wait_on_futures_map(futures):
    for future in futures.values():
        future.result()
        assert future.done()
