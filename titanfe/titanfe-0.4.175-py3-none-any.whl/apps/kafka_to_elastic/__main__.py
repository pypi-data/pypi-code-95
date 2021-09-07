"""
kafka_to_elastic

Usage:
  kafka_to_elastic [-k <bootstrap_servers>] [-e <elastic_host>] [-s <service_topics>] -t [<topics>]
  kafka_to_elastic (-h | --help)

Example:
  kafka_to_elastic --kafka 127.0.0.1:9092 --elastic 127.0.0.1 -t a_topic another_topic

Options:
  -h, --help     Show this screen.

  -k <bootstrap_servers>, --kafka=<bootstrap_servers>
      the Kafka bootstrap_servers to connect to as `<host>:<port> <host:port> ...`
      [default: 10.14.0.23:9092]

  -e <elastic_host>, --elastic=<elastic_host>
      the elastic host `<hostname_or_ip>` [default: 10.14.0.21]

  -s <service_topics>, --service-topics=<service_topics>
      topics of titan service logs `<one or more topics>` [default: titan.servicelogs]

  -t <flowengine_topics>, --flowengine-topics=<flowengine_topics>
      topics of titan service logs `<one or more topics>` [default: titanfe.metrics]
"""

# pylint: disable=broad-except, missing-docstring
# missing-function-docstring, missing-class-docstring
import argparse
import os
import asyncio
import pickle
import json
import signal
from contextlib import suppress
from datetime import datetime
from collections import namedtuple
from aiokafka import AIOKafkaConsumer, ConsumerStoppedError
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

KafkaTopics = namedtuple("KafkaTopics", ("name", "type"))
SERVICE_TOPIC_TYPE = "service"
FLOWENGINE_TOPIC_TYPE = "flowengine"


async def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-e",
        "--elastic",
        type=str,
        default="10.14.0.21",
        help=" the elastic host `<hostname_or_ip>`",
    )
    arg_parser.add_argument(
        "-k",
        "--kafka",
        type=str,
        default="10.14.0.23:9092",
        help=" the Kafka bootstrap_servers to connect to as `<host>:<port> <host:port> ...`",
    )
    arg_parser.add_argument(
        "-s",
        "--service-topics",
        nargs="+",
        default=["titan.servicelog"],
        help="topics of titan go service logs `<one or more topics>` [default: titan.servicelogs]",
    )
    arg_parser.add_argument(
        "-t",
        "--topics",
        nargs="+",
        default=["titanfe.metrics"],
        help="topics of the flowengine logs`<one or more topics>` [default: titanfe.metrics]",
    )
    args = arg_parser.parse_args()

    signals = signal.SIGINT, signal.SIGTERM

    if os.name != "nt":  # not available on windows
        signals += (signal.SIGHUP,)  # pylint: disable=no-member

    for sign in signals:
        signal.signal(sign, schedule_shutdown)

    bootstrap_servers = args.kafka
    elastic_host = args.elastic
    topics = KafkaTopics(
        name=args.topics + args.service_topics,
        type={
            **{topic: FLOWENGINE_TOPIC_TYPE for topic in args.topics},
            **{topic: SERVICE_TOPIC_TYPE for topic in args.service_topics},
        },
    )

    print("Reading", topics.name, "From", bootstrap_servers, "To", elastic_host)

    async with KafkaReader(topics.name, bootstrap_servers=bootstrap_servers) as kafka, \
            ElasticWriter(elastic_host=elastic_host) as elastic:  # pylint: disable= ; noqa
        async for topic, records in kafka.read():
            len_records = f"{len(records)} record{'s' if len(records) > 1 else ''}"
            print(f"processing {len_records} from {topic.topic} of type {topics.type[topic.topic]}")
            msgs = list(transform_kafka_to_elastic(records, topics.type[topic.topic]))
            await elastic.bulk_insert(msgs)


def schedule_shutdown(sign, _):
    print(f"Received {signal.Signals(sign).name} ...")  # pylint: disable=no-member

    async def shutdown():
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()

        print(f"Cancelling outstanding tasks ({len(tasks)})")
        await asyncio.gather(*tasks)

    asyncio.create_task(shutdown())


class KafkaReader:
    def __init__(self, topics, bootstrap_servers):
        self.consumer = AIOKafkaConsumer(
            *topics,
            loop=asyncio.get_event_loop(),
            bootstrap_servers=bootstrap_servers,
            # auto_offset_reset='earliest',
        )

    async def start(self):
        await self.consumer.start()

    async def stop(self):
        await self.consumer.stop()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    def __aiter__(self):
        return self

    async def __anext__(self):
        while True:
            try:
                batch = await self.consumer.getmany(timeout_ms=1000)
            except (asyncio.CancelledError, ConsumerStoppedError):
                raise StopAsyncIteration

            if not batch:
                print(".", end="", flush=True)
                continue

            return batch

    async def read(self):
        async for batch in self:
            for topic, records in batch.items():
                yield topic, records


class ElasticWriter:
    def __init__(self, elastic_host):
        self.elastic = AsyncElasticsearch(hosts=[{"host": elastic_host}])

    async def __aenter__(self):
        await self.elastic.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.elastic.close()

    async def bulk_insert(self, document_generator):
        await async_bulk(self.elastic, document_generator)


def transform_kafka_to_elastic(batch, topic_type):
    def transform(message):
        content = pickle.loads(message.value)
        content["@timestamp"] = content.pop("timestamp")

        doc_type = content["content_type"]
        index = f"{doc_type}-{datetime.now():%Y-%m-%d}"

        return {"_op_type": "index", "_index": index, "_type": doc_type, "_source": content}

    def transform_service_log(message):
        content = json.loads(message.value)
        content["@timestamp"] = content.pop("time")
        package = content["package"].split("/")[0]
        index = f"{package.lower()}-{datetime.now():%Y-%m-%d}"

        return {"_op_type": "index", "_index": index, "_type": "service", "_source": content}

    for message in batch:
        try:
            if topic_type == SERVICE_TOPIC_TYPE:
                yield transform_service_log(message)
            else:
                yield transform(message)

        except Exception as error:
            print("Failed to transform ", message, error)


if __name__ == "__main__":

    async def run_main():
        try:
            with suppress(asyncio.CancelledError):
                await main()
        except Exception as error:
            print("Error:", repr(error))

    asyncio.run(run_main())
