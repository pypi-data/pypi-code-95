#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""An output Port of a Brick to connect to and receive data from"""

import asyncio

from .group import ConsumerGroup


class Port:
    """"A port holds a consumer group for each brick connected to the port in a flow.
        The consumer group holds at least one connection with the succeeding brick.
        Should the succeeding brick scale connections are added to the consumer group
        when new instances of the brick come online"""

    def __init__(self, name):
        self.name = name
        self.consumer_groups = {}

    def add_consumer_group(self, consumer_instance_id, queue, consumer, logger):
        """add a new consumer group"""
        if consumer_instance_id not in self.consumer_groups:
            group = ConsumerGroup(consumer_instance_id, queue, consumer, logger)
            self.consumer_groups[consumer_instance_id] = group

    def add_consumer(self, consumer):
        group = self.consumer_groups[consumer.brick_instance_id]
        group.add(consumer)

    async def enqueue(self, packet):
        if self.consumer_groups:
            await asyncio.wait({group.enqueue(packet) for group in self})

    async def close(self):
        if self.consumer_groups:
            await asyncio.wait({group.close() for group in self})

    def __iter__(self):
        return iter(self.consumer_groups.values())

    def __repr__(self):
        return f"Port(name={self.name}, consumer_groups={self.consumer_groups})"
