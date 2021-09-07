#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Subscribe to Kafka Topics and print the messages to the console"""

import argparse
import logging
import sys

from kafka import KafkaConsumer

logging.basicConfig(
    stream=sys.stdout,
    # level=logging.DEBUG,
    level=logging.INFO,
)
log = logging.getLogger(__name__)


def print_log_stream(kafka_host, topics):
    """get and print the messages from the topic"""
    consumer = KafkaConsumer(
        *topics.split(), group_id="test", bootstrap_servers=kafka_host, auto_offset_reset="earliest"
    )
    for msg in consumer:
        print(msg)


def main():
    """parse args and run the application"""
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-topics", help="list of topics 'topic1 topic2", default="titanfe.metrics titanfe.logs",
    )
    arg_parser.add_argument(
        "-kafka",
        help="Kafka bootstrap servers",
        # default="localhost:9092",
        # default="192.168.171.131:9092",
        default="10.14.0.23:9092",
    )
    args = arg_parser.parse_args()
    print_log_stream(args.kafka, args.topics)


if __name__ == "__main__":
    main()
