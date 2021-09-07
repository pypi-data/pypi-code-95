#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""The actual brick runner"""

import asyncio
import json
import os
import signal
from datetime import datetime, timedelta

from titanfe import log as logging
from titanfe.connection import Connection
from titanfe.messages import Message
from titanfe.utils import cancel_tasks, get_ip_address
from .brick import Brick
from .grid_manager import GridManager
from .input import Input
from .metrics import MetricEmitter
from .output import Output, Consumer, ConsumerGroup
from .packet import Packet
from ..control_peer.brick import BrickInstanceDefinition
from ...config import configuration


class BrickRunner:
    """The BrickRunner will create an Input, get a setup from the control peer,
       create corresponding outputs and then start processing packets from the input.

    Arguments:
        uid (str): a unique id for the runner
    """

    def __init__(self, uid):
        self.uid = uid
        self.log = logging.TitanPlatformLogger(
            f"{__name__}.{self.uid}", context=logging.global_context
        )
        self.loop = asyncio.get_event_loop()

        # done async in setup
        self.input = None
        self.output = None
        self.brick = None
        self.server = None
        self.address = (None, None)
        self.gridmanager = None

        self.setup_completed = asyncio.Event()

        self.idle_since = None
        self.metric_emitter = None
        self.tasks = []

    @classmethod
    async def create(cls, uid, brick_definition: BrickInstanceDefinition):
        """Creates a brick runner instance and does the initial setup phase before returning it"""
        br = cls(uid)  # pylint: disable=invalid-name
        await br.setup(brick_definition)
        return br

    async def setup(self, brick_definition: BrickInstanceDefinition):
        """does the inital setup parts that have to be awaited"""
        self.log = logging.TitanPlatformLogger(
            f"{__name__}.{self.uid}.{brick_definition.name}", context=logging.global_context
        )

        await self.start_server()

        self.metric_emitter = await MetricEmitter.create_from_brick_runner(self)
        self.brick = Brick(brick_definition, self.metric_emitter, self.log)
        self.metric_emitter.set_metadata_from_runner(self)

        self.gridmanager = GridManager(self.uid, self.brick.uid)
        ConsumerGroup.slow_queue_alert_callback = self.gridmanager.request_scaling

        self.input = Input(self)
        self.output = await Output.create(self.log, self.metric_emitter)
        available_input_sources = await self.gridmanager.register_runner(self.address)
        if available_input_sources:
            self.log.debug("input sources %s", available_input_sources)
            self.input.add_sources(available_input_sources)

        if not self.brick.is_outlet:
            self.output.make_ports_and_groups(brick_definition.connections.output)
            self.tasks.append(asyncio.create_task(self.output_results()))

        self.add_signal_handlers()

        self.setup_completed.set()

    async def run(self):
        """process items from the input"""
        self.log.with_context.info("Start runner: %s", self.uid)

        if self.brick.is_inlet:
            # trigger processing
            await self.input.put(Packet(port="TRIGGER"))

        if not self.brick.is_inlet:
            self.tasks.append(asyncio.create_task(self.exit_when_idle()))

        try:
            await self.process_input()
        except Exception:  # pylint: disable=broad-except
            self.log.with_context.error("Brick failed", exc_info=True)

        self.log.with_context.info("Exit")

    async def start_server(self):
        """start server"""
        self.server = await asyncio.start_server(
            self.handle_incoming_connection, host=configuration.IP or get_ip_address()
        )
        self.address = self.server.sockets[0].getsockname()

    async def handle_incoming_connection(self, reader, writer):
        """create consumers for incoming connections and dispatch the connection to them"""
        await self.setup_completed.wait()

        connection = Connection(reader, writer, self.log)

        # We can remove this once the Gridmanager starts sending UJO Messages
        try:
            msg_len = await connection.reader.readexactly(4)
        except (asyncio.IncompleteReadError, ConnectionError):
            self.log.debug("Stream at EOF - close connection.")
            # self.log.debug('', exc_info=True)
            await connection.close()
            return

        rawmsg = await connection.reader.readexactly(int.from_bytes(msg_len, "big"))

        try:
            msg = connection.decode(rawmsg)
            message = Message(*msg)
        except TypeError:
            self.log.error("Received unknown Message format: %s", rawmsg)
            return
        except Exception:  # pylint: disable=broad-except
            # self.log.error("Failed to decode %r", msg, exc_info=True)
            # raise ValueError(f"Failed to decode {msg}")
            # TODO: # Use UJO Encoding and appropriate msg format in GridManager
            self.log.info("new input source available: %s", json.loads(rawmsg))
            self.input.add_source(json.loads(rawmsg))
        else:
            self.log.info("new consumer entered: %s", message.content)
            brick_instance_id, port = message.content
            self.output[port].add_consumer(Consumer(port, brick_instance_id, connection))

    async def process_input(self):
        """ get packets from the input and process them """
        with self.brick:
            async for packet in self.input:
                packet.update_input_exit()
                self.log.debug("process packet: %s", packet)
                await self.brick.process(packet)
                self.idle_since = None

    def schedule_shutdown(self, sig, frame):  # pylint: disable=unused-argument
        self.log.info(
            "Received signal %s - scheduling shutdown",
            signal.Signals(sig).name,  # pylint: disable=no-member
        )  # pylint: disable=no-member
        asyncio.create_task(self.shutdown())

    def add_signal_handlers(self):
        signals = (signal.SIGINT, signal.SIGTERM)
        if os.name == "nt":
            signals += (signal.SIGBREAK,)  # pylint: disable=no-member
        for sig in signals:
            signal.signal(sig, self.schedule_shutdown)

    async def stop_processing(self):
        """stop processing bricks"""
        self.log.info("Stop Processing")
        await self.gridmanager.deregister_runner()
        logging.flush_kafka_log_handler()
        await self.input.close()
        self.brick.terminate()
        self.server.close()
        await self.server.wait_closed()
        await self.output.close()
        await self.metric_emitter.stop()

    async def shutdown(self):
        """shuts down the brick runner"""
        self.log.with_context.info("Initiating Shutdown")
        await self.stop_processing()
        await cancel_tasks(self.tasks, wait_cancelled=True)

    async def output_results(self):
        """get results from the brick execution and add them to the output queues of this runner"""
        async for packet, port in self.brick.get_results():
            packet.update_output_entry()
            await self.output[port].enqueue(packet)

    @property
    def is_idle(self):
        return self.input.is_empty and self.output.is_empty and not self.brick.is_processing

    async def exit_when_idle(self):
        """Schedule as task to initiate shutdown if the configured maximum idle time is reached"""
        if not self.brick.exit_after_idle_seconds:
            return  # deactivated

        # check at least once per second:
        interval = min(self.brick.exit_after_idle_seconds * 0.1, 1)

        self.idle_since = None
        idle_time = timedelta(seconds=0)
        max_idle_time = timedelta(seconds=self.brick.exit_after_idle_seconds)

        while idle_time <= max_idle_time:
            await asyncio.sleep(interval)
            if not self.is_idle:
                self.idle_since = None
                continue

            if self.idle_since is None:
                self.idle_since = datetime.now()
                continue

            idle_time = datetime.now() - self.idle_since

        self.log.with_context.info("Max idle time reached. Scheduling shutdown")
        asyncio.create_task(self.shutdown())
