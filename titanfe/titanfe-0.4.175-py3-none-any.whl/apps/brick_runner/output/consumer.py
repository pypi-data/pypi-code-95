#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""a Consumer represents a connection made to the output server"""

import asyncio

from titanfe.utils import create_uid


class Consumer:
    """wrap incoming connections and handle sending packets"""

    def __init__(self, port_name, brick_instance_id, connection):
        self.uid = create_uid(f"C-{brick_instance_id}-")
        self.port_name = port_name
        self.brick_instance_id = brick_instance_id
        self.connection = connection

        self.listener = asyncio.create_task(self.listen())
        self._packets_expected = 0
        self._receptive = asyncio.Event()

        self.disconnected = asyncio.Event()

    def __repr__(self):
        return (
            f"Consumer("
            f"uid={self.uid}, "
            f"port_name={self.port_name}, "
            f"brick_instance_id={self.brick_instance_id})"
        )

    async def is_receptive(self):
        await self._receptive.wait()
        return self

    async def listen(self):
        """wait for packet requests, set disconnected-Event if the connection gets closed"""
        async for message in self.connection:
            self._packets_expected += message.content
            self._receptive.set()

        self.disconnected.set()
        self._receptive.clear()

    async def close_connection(self):
        self.listener.cancel()
        await self.connection.close()

    async def send(self, packet):
        """send a packet"""
        self._packets_expected -= 1
        if self._packets_expected == 0:
            self._receptive.clear()

        packet.update_output_exit()
        await self.connection.send(packet.as_message())
