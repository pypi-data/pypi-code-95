#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""The INPUT side of a brick (runner)"""

import asyncio
from asyncio import futures, CancelledError
from functools import partial

from titanfe.connection import Connection
from titanfe.messages import PacketRequest, ConsumerRegistration
from titanfe.utils import cancel_tasks
from .metrics import QueueWithMetrics
from .packet import Packet


class Input:
    """The Input side of a brick runner requests new packets from the previous BrickRunners
    OutputServer until it's QueueLimit is exceeded and again once the "low level" is reached.
    The Input will also emit queue metrics every 0.1 sec if there are packets in the queue.

    Arguments:
        runner (BrickRunner): instance of a parent brick runner
        adress (NetworkAddress): (host, port) of the source-BrickRunners OutputServer
    """

    def __init__(self, runner):
        self.name = f"Input.{runner.brick.name}"
        self.runner = runner
        self.log = runner.log.getChild("Input")

        self.metric_emitter = runner.metric_emitter
        self.metric_task = None

        self.receivers = []
        self.packets = QueueWithMetrics(runner.metric_emitter, self.name)

        self.batch_size = 25
        self.low_queue_level = 10
        self.at_low_queue_level = asyncio.Event()
        self.at_low_queue_level.set()

        self._close = False
        self._getter = None

    def __aiter__(self):
        return self

    async def __anext__(self) -> Packet:
        while not self._close:
            self._getter = asyncio.create_task(self.get())
            try:
                # careful: without timeout the get sometimes hangs on `self.packets.get()`
                #          in that case the brick runner does not shutdown correctly.
                # TODO: find out if there's a better way...
                return await asyncio.wait_for(self._getter, timeout=2)
            except CancelledError:
                raise StopAsyncIteration
            except futures.TimeoutError:
                pass  # retry or abort if closing...
        raise StopAsyncIteration

    async def get(self):
        """awaitable to get the next available packet from the input queue"""
        packet = await self.packets.get()
        self.packets.task_done()
        if self.packets.qsize() <= self.low_queue_level:
            self.at_low_queue_level.set()

        packet.update_input_exit()
        return packet

    async def put(self, packet):
        packet.update_input_entry()
        await self.packets.put(packet)
        if self.packets.qsize() > self.low_queue_level:
            self.at_low_queue_level.clear()

    def add_sources(self, sources):
        for source in sources:
            self.add_source(source)

    def add_source(self, source):
        port_name, target_port = source["port"], source["target_port"]
        address = source["address"].split(":")
        task = asyncio.create_task(self.get_input(address, port_name, target_port))
        self.receivers.append(task)
        task.add_done_callback(partial(self.handle_input_loss, address, port_name))

    def handle_input_loss(self, address, port_name, task):
        """
        if we loose a connection to some input source, we handle removing the appropriate task here.
        Any CancelledError will be ignored, all others Exceptions are unexpected and will be logged.
        """
        self.receivers.remove(task)
        try:
            task.result()
        except CancelledError:
            pass
        except Exception as error:  # pylint: disable=broad-except
            self.log.error("Error on input connection: %r on %s -> %s", port_name, address, error)

    async def get_input(self, address, port_name, target_port):
        """Connect to and retrieve packets from the given address"""
        async with await Connection.open(address) as connection:
            await connection.send(ConsumerRegistration(content=(self.runner.brick.uid, port_name)))

            while True:
                await asyncio.sleep(0)  # be cooperative
                await self.at_low_queue_level.wait()
                await connection.send(PacketRequest(self.batch_size))
                for _ in range(self.batch_size):
                    message = await connection.receive()
                    if not message:
                        return  # disconnected
                    packet = Packet.from_dict(message.content)
                    packet.port = target_port
                    await self.put(packet)

    async def close(self):
        """Stop the input"""
        if self.receivers:
            await cancel_tasks(self.receivers)
        self._close = True
        if self._getter:
            self._getter.cancel()
        await self.packets.close()

    @property
    def is_empty(self):
        return not self.packets.unfinished_tasks
