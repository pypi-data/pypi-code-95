#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

import json
import logging
import time
import uuid
import os
from mobio.libs.Singleton import Singleton
from confluent_kafka.cimpl import Producer

logger = logging.getLogger()


class Message(dict):
    def __init__(self, message=None):
        if message and isinstance(message, dict):
            super().__init__(message)
        else:
            super().__init__()

        if 'meta' not in self:
            self.__setitem__('meta', {
                'message_id': str(uuid.uuid4()),  # request ID used to trace the data flow
                'message_timestamp': int(time.time() * 1000),
            })


@Singleton
class KafkaUtil:
    producer = None

    def __init__(self):
        conf = {
            'bootstrap.servers': os.environ.get('KAFKA_BROKER'),
        }
        self.producer = Producer(conf)

    def produce(self, topic, message: Message, callback=None):
        if not isinstance(message, Message):
            raise TypeError('Invalid message type')

        try:
            if not callback:
                self.producer.produce(
                    topic,
                    json.dumps(message).encode('utf8'),
                    callback=KafkaUtil.kafka_delivery_callback,
                )
            else:
                self.producer.produce(
                    topic,
                    json.dumps(message).encode('utf8'),
                    callback=callback,
                )
        except BufferError:
            logger.error('%% Local producer queue is full (%d messages awaiting delivery): try again',
                         len(self.producer))
            self.producer.poll(0)

        self.producer.flush()

    @staticmethod
    def kafka_delivery_callback(err, msg):
        if err:
            logger.error('Message failed delivery: %s', err)
        else:
            logger.info('Message delivered to %s [%d] @ %d', msg.topic(), msg.partition(), msg.offset())
