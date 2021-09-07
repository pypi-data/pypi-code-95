#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""
Fixtures for BrickRunner-Tests
"""

# pylint: disable=redefined-outer-name, too-few-public-methods
import asyncio
import inspect
import logging
import queue
import sys
import threading
from typing import Union
from unittest.mock import MagicMock

import janus

from titanfe.apps.brick_runner.brick import Brick
from titanfe.apps.brick_runner.packet import Packet
from titanfe.apps.brick_runner.runner import BrickRunner
from titanfe.apps.control_peer.brick import BrickInstanceDefinition
from titanfe.brick import InletBrickBase
from titanfe.constants import DEFAULT_PORT
from titanfe.log import TitanPlatformLogger
from titanfe.utils import create_uid

logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(name)s --> %(message)s",
    level=logging.DEBUG,
)

LOG = TitanPlatformLogger(__name__)


async def async_magic():
    pass


# extend the mock object to be awaitable
MagicMock.__await__ = lambda *args, **kwargs: async_magic().__await__()


class MetricEmitterDummy(MagicMock):
    """a dummy emitter"""

    # pylint: disable=too-few-public-methods

    log = MagicMock()
    kafka = MagicMock()


class GridManagerDummy:
    """Mocks the Gridmanager connection"""

    # pylint: disable=too-few-public-methods

    request_scaling = MagicMock()
    deregister_runner = MagicMock()
    register_runner = MagicMock()


class Input:
    """TestRunner: Input replacement"""

    def __init__(self):
        self.queue = janus.Queue()
        self.packets = self.queue.async_q

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
                return await asyncio.wait_for(self._getter, timeout=0.05)
            except asyncio.CancelledError:
                raise StopAsyncIteration
            except asyncio.TimeoutError:
                pass  # retry
        raise StopAsyncIteration

    async def get(self):
        """awaitable to get the next available packet from the input queue"""
        packet = await self.packets.get()
        if not isinstance(packet, Packet):
            payload, port = packet
            packet = Packet(port=port, payload=payload)

        self.packets.task_done()

        packet.update_input_exit()
        return packet

    async def put(self, item):
        return await self.packets.put(item)

    async def close(self):
        """Stop the input"""
        self.sync_close()

    def sync_close(self):
        self._close = True
        if self._getter:
            self._getter.cancel()
        self.queue.close()

    @property
    def is_empty(self):
        return self.packets.empty()


class Output(queue.Queue):
    """TestRunner: Output replacement"""
    @property
    def is_empty(self):
        return self.empty()

    async def close(self):
        pass


class TestRunner:
    """A TestRunner for easy integration tests of your Bricks.

    runs an actual (though modified) BrickRunner in a separate thread,
    so you are not coerced into using asyncio.

    Parameters:
        brick_class_or_path_to_module:
            pass either your Brick class or a path to your module which must have a `.Brick`
        parameters:
            a dict with parameters for your Brick
        log_level:
            a LOG_LEVEL understood by python's logging module e.g. logging.DEBUG or "DEBUG"
            the default level is set to logging.ERROR

    Usage:
        ```
        runner = TestRunner(Brick, parameters={...})
        runner.start()
        runner.input.put(UjoInt32(42))
        port, output = runner.output.get()
        runner.stop()
        ```

        or simpler:
        ```
        with TestRunner(Brick, parameters={...}) as runner:
            runner.input.put(UjoInt32(42))
            port, output = runner.output.get()
        ```
    """

    __test__ = False  # pytest: do not try to collect this.

    def __init__(
        self,
        brick_class_or_path_to_module: Union["Brick", str],
        parameters: dict,
        log_level: Union[int, str] = logging.ERROR,
    ):
        LOG.setLevel(log_level)
        self.uid = create_uid("Test-")
        self.thread = threading.Thread(target=self.run_async_create_and_run)
        self.output = queue.Queue()
        self.terminate = threading.Event()

        self.runner = BrickRunner("R-TestRunner")
        self.setup_completed = threading.Event()

        self.brick_class_or_path_to_module = brick_class_or_path_to_module
        self.parameters = parameters

        self.definition = {
            "Configuration": {
                "instanceId": "B-1",
                "name": "Brick-" + self.uid,
                "brick": "Test",
                "id": self.uid,
                "family": "Test",
                "parameters": {},
                "autoscale_queue_level": 25,
                "autoscale_max_instances": 1,
                "exit_after_idle_seconds": 0,
                "inputPorts": [],
                "outputPorts": [],
            },
            "FlowID": self.uid,
            "FlowName": self.uid,
            "FlowSchema": "fixme",
            "Inbound": {},
            "Outbound": {
                DEFAULT_PORT: [{"InstanceID": "dummy", "autoscale_queue_level": 0, "Port": "Input"}]
            },
        }

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    async def check_terminate(self, runner):
        while not self.terminate.is_set():
            await asyncio.sleep(0.2)
        runner.brick.terminate()

    def run_async_create_and_run(self):
        asyncio.run(
            self._create_and_run_runner(self.brick_class_or_path_to_module, self.parameters)
        )

    async def _create_and_run_runner(
        self, brick_class_or_path_to_module, parameters
    ):
        runner = self.runner
        runner.gridmanager = GridManagerDummy()
        runner.metric_emitter = MetricEmitterDummy()
        runner.server = MagicMock()
        runner.input = Input()
        runner.output = Output()

        is_brick = (
            inspect.isclass(brick_class_or_path_to_module)
            and brick_class_or_path_to_module.__name__ == "Brick"
        )

        instance_definition = BrickInstanceDefinition.from_gridmanager(self.definition)

        if is_brick:
            instance_definition.base.module_path = "sys"
        else:
            instance_definition.base.module_path = brick_class_or_path_to_module

        instance_definition.processing_parameters.update(**parameters)

        runner.brick = Brick(instance_definition, runner.metric_emitter, LOG)

        if is_brick:

            class Wrapper:
                Brick = brick_class_or_path_to_module

            runner.brick.module = Wrapper()

        runner.brick.is_inlet = issubclass(runner.brick.module.Brick, InletBrickBase)

        runner.tasks.append(asyncio.create_task(self.output_results()))
        runner.tasks.append(asyncio.create_task(self.check_terminate(runner)))

        runner.setup_completed.set()
        self.setup_completed.set()

        try:
            await runner.run()
        except TypeError:
            # TODO: figure out why `self.input` is occasionally None during brickrunner.shutdown()
            #       of course then `await self.input.close()` fails :/
            pass
        while not self.terminate.is_set():
            await asyncio.sleep(0.1)

    @property
    def input(self):
        """add input on the default port by calling `input.put()`,
        for explicit ports use `input["<PortName>"].put()`"""
        if not self.thread.is_alive():
            raise UserWarning("Input unavailable until runner is started")

        self.setup_completed.wait()

        runner = self.runner

        class PortProxy:
            def __init__(self, name):
                self.name = name

            def put(self, item):
                runner.input.queue.sync_q.put((item, self.name))

        class InputProxy:
            """To get port/payload into the running runner..."""
            @staticmethod
            def put(item):
                runner.input.queue.sync_q.put((item, DEFAULT_PORT))

            @staticmethod
            def __getitem__(name):
                return PortProxy(name)

        return InputProxy()

    async def output_results(self):
        """get results from the brick execution and add them to the output queues of this runner"""
        async for packet, port in self.runner.brick.get_results():
            self.output.put((port, packet.payload))

    def start(self):
        self.thread.start()

    def stop(self):
        self.runner.input.sync_close()
        self.terminate.set()
        self.thread.join()
