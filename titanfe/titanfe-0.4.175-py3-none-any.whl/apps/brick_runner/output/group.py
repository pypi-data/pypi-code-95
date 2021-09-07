#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Group represents multiple consumers of the same type"""

import asyncio
from asyncio import CancelledError
from collections import deque
from copy import deepcopy
from dataclasses import dataclass, field
from typing import List

from UJOSchema import schema_to_type
from ujotypes.variants.none import UJO_VARIANT_NONE

from titanfe.apps.brick_runner.connection import BufferDescription, MappingRules
from titanfe.apps.brick_runner.metrics import QueueWithMetrics
from titanfe.utils import cancel_tasks, pairwise, Flag


@dataclass
class ConsumerGroupTasks:
    """Task of a Consumer group"""

    send_packets: asyncio.Task
    check_scaling: asyncio.Task
    handle_disconnects: field(default_factory=List)

    @property
    def all_tasks(self):
        return self.handle_disconnects + [self.send_packets, self.check_scaling]

    def __iter__(self):
        return iter(self.all_tasks)

    def add_disconnect_handler(self, on_disconnect: asyncio.coroutine):
        task = asyncio.create_task(on_disconnect)
        self.handle_disconnects.append(task)
        task.add_done_callback(self.handle_disconnects.remove)

    async def cancel(self):
        await cancel_tasks(self)


class ConsumerGroup:
    """Group consumers of same type and distribute packets between them"""

    slow_queue_alert_callback = lambda *args, **kwargs: None  # noqa

    def __init__(self, consumer_instance_id, queue, consumer, logger):
        self.name = consumer_instance_id
        self.log = logger
        self.consumers = []
        self.packets: QueueWithMetrics = queue
        self.has_packets = Flag()
        self.has_consumers = Flag()
        self.new_consumer_entered = Flag()

        self.autoscale_queue_level = consumer.get("autoscale_queue_level", 0)
        target_port = consumer.get("targetPort")
        self.target = (
            schema_to_type(target_port["schema"], target_port["typeName"])
            if target_port.get("schema", None)
            else UJO_VARIANT_NONE
        )
        self.buffer_description = BufferDescription(consumer["buffer"])
        self.mapping = MappingRules(consumer["mapping"])

        self.tasks = ConsumerGroupTasks(
            asyncio.create_task(self.send_packets()),
            asyncio.create_task(self.check_scaling_required(self.autoscale_queue_level)),
            [],
        )

    def __iter__(self):
        return iter(self.consumers)

    def __repr__(self):
        return f"Group(name={self.name}, consumers={self.consumers})"

    async def close(self):
        await asyncio.gather(*[consumer.close_connection() for consumer in self])
        await self.tasks.cancel()
        await self.packets.close()

    async def check_scaling_required(self, autoscale_queue_level=0, check_interval=0.2):
        """ watch the queue and dispatch an alert if it grows continuously,
            then wait for a new consumer before resetting the queue history - repeat."""
        try:
            if not autoscale_queue_level or not self.slow_queue_alert_callback:
                return

            await self.has_packets.wait()
            await self.slow_queue_alert_callback(self.name)

            # wait for the first consumer to come in
            await self.new_consumer_entered.wait()
            self.new_consumer_entered.clear()

            history = deque(maxlen=5)

            while True:
                await asyncio.sleep(check_interval)
                current_queue_size = self.packets.qsize()
                history.append(current_queue_size)

                if current_queue_size < autoscale_queue_level or len(history) < 3:
                    continue

                queue_is_growing = all(0 < prev <= curr for prev, curr in pairwise(history))
                if queue_is_growing:
                    await self.slow_queue_alert_callback(self.name)
                    await self.new_consumer_entered.wait()

                self.new_consumer_entered.clear()
                history.clear()
        except CancelledError:
            return

    def add(self, consumer):
        self.consumers.append(consumer)
        self.has_consumers.set()
        self.new_consumer_entered.set()
        self.tasks.add_disconnect_handler(self.handle_disconnect(consumer))

    async def handle_disconnect(self, consumer):
        """handle a consumer disconnecting"""
        await consumer.disconnected.wait()
        self.consumers.remove(consumer)
        if not self.consumers:
            self.has_consumers.clear()
            await cancel_tasks([self.tasks.check_scaling])
            self.tasks.check_scaling = asyncio.create_task(
                self.check_scaling_required(self.autoscale_queue_level)
            )

    async def enqueue(self, packet):
        """enqueue the bricks packet after applying the connections
        mapping rules and updating its buffer"""

        packet = deepcopy(packet)

        try:
            packet.buffer.update_from_result(
                result=packet.payload, buffer_description=self.buffer_description
            )
        except Exception as err:  # pylint: disable=broad-except
            self.log.error(f"updating buffer failed: {err}")
            return

        try:
            next_input = self.mapping.apply(
                buffer=packet.buffer, source=packet.payload, target=deepcopy(self.target)
            )
        except Exception as err:  # pylint: disable=broad-except
            self.log.error(f"mapping failed: {err!r}")
            return

        packet.payload = next_input

        await self.packets.put(packet)
        self.has_packets.set()

    async def send_packets(self):
        """send packets"""
        while True:
            while not (self.has_consumers and self.has_packets):
                await self.has_consumers.wait()
                await self.has_packets.wait()

            consumer = await self.get_receptive_consumer()
            packet = self.packets.get_nowait()
            if self.packets.empty():
                self.has_packets.clear()

            await consumer.send(packet)
            self.packets.task_done()

    async def get_receptive_consumer(self):
        """wait until any of the consumers is ready to receive and then return it"""
        done, pending = await asyncio.wait(
            {consumer.is_receptive() for consumer in self}, return_when=asyncio.FIRST_COMPLETED
        )
        await cancel_tasks(pending)
        return done.pop().result()

    @property
    def has_unfinished_business(self):
        return self.packets.unfinished_tasks
