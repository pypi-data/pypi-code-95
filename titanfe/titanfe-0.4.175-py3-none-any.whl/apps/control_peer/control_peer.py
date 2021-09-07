#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""the actual control peer"""

import asyncio
import signal
from collections import defaultdict
from concurrent.futures.thread import ThreadPoolExecutor

from titanfe import log as logging
from titanfe.log import TitanLogAdapter, FlowContext
from .services import package_manager, grid_manager, ServiceError
from .brick import BrickBaseDefinition
from .runner import BrickRunner
from .webapi import WebApi

log = logging.TitanPlatformLogger(__name__)


class ControlPeer:
    """The control peer application will start runners as required for the flows/bricks
       as described in the given config file. Once the runners have registered themselves,
       they will get according assignments.
    """

    def __init__(self):
        logging.initialize(service="ControlPeer")

        self.loop = asyncio.get_event_loop()

        self.runners = {}
        self.runners_by_flow = defaultdict(set)

        self.api = WebApi(self)

        self.tasks = {}

    @classmethod
    def create(cls):
        """"Create control peer"""
        control_peer = cls()
        control_peer.install_signal_handlers()

        return control_peer

    def install_signal_handlers(self):
        signals = signal.SIGINT, signal.SIGTERM

        for sig in signals:
            signal.signal(sig, self.schedule_shutdown)

    async def run(self):
        """run the application"""
        server = asyncio.create_task(self.api.serve())
        try:
            await package_manager.register(self.api.address)
            await self.install_bricks()
            await grid_manager.register(self.api.address)
        except ServiceError as service_error:
            log.error("Error: %s - Shutting down.", service_error)
        else:
            await server

        log.info("Exit")

    def schedule_shutdown(self, sig, _):
        log.info(
            "Received signal %s - scheduling shutdown",
            signal.Signals(sig).name,  # pylint: disable=no-member
        )
        asyncio.create_task(self.shutdown())

    async def shutdown(self):
        """shut down the controlpeer"""
        await package_manager.deregister(self.api.address)
        await grid_manager.deregister(self.api.address)
        await self.api.stop()
        await self.stop_runners()

        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        log.debug("Cancelling outstanding tasks (%s)", len(tasks))

        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks)

    async def install_bricks(self):
        """get brick list from PackageManager and install bricks if necessary"""
        bricks = await package_manager.get_bricks()
        if not bricks:
            return

        def install_or_update(brick):
            async def main(brick):
                await BrickBaseDefinition(
                    uid=brick.get("id"),
                    last_modified=brick.get("lastmodified"),
                    name=brick.get("name"),
                    logger=log,
                ).install_or_update()

            asyncio.run(main(brick))

        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor()
        await asyncio.wait(
            {loop.run_in_executor(executor, install_or_update, brick) for brick in bricks}
        )

    async def start_new_runner(self, brick):
        """update the configuration and start the flow"""
        if brick.base.uid in self.tasks:
            # wait until installation is done, before starting the runner
            try:
                task = self.tasks.pop(brick.base.uid)
            except KeyError:
                pass  # unlikely, but the task may have finished and removed itself
            else:
                await task

        try:
            runner = BrickRunner(brick, on_termination_cb=self.remove_runner)
            runner.start()
        except Exception as error:  # pylint: disable=broad-except
            logger = TitanLogAdapter(log, extra=FlowContext.from_brick(brick).asdict())
            logger.error("Failed to start runner for: %s", brick, exc_info=True)
            raise error

        self.runners[runner.uid] = runner
        self.runners_by_flow[brick.flow.uid].add(runner)

    def remove_runner(self, runner):
        log.debug("Runner %s terminated - remove.", runner)
        self.runners.pop(runner.uid)
        flow_runners = self.runners_by_flow.get(runner.brick.flow.uid, set())
        flow_runners.discard(runner)

    async def stop_runners(self, flow_uid=None):
        """ stop all runners or all runners for the given flow.uid """
        if flow_uid:
            log.debug("Stopping brick runners for Flow: %s", flow_uid)
            runners = self.runners_by_flow.pop(flow_uid, set())
        else:
            log.debug("Stopping all runners")
            runners = self.runners.values()

        await asyncio.gather(*[runner.stop() for runner in runners])
