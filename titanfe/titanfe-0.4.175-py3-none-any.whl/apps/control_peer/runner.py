#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Encapsulate brick runner related things"""
import asyncio
import os
import pickle
import signal
import subprocess

from titanfe import log as logging
from titanfe.config import configuration
from titanfe.utils import create_uid, Flag


class BrickRunner:
    """The BrickRunner can be used to start brick runner processes and hold corresponding data

    Arguments:
        controlpeer_address (NetworkAddress): the address on which the control peer is listening
    """

    def __init__(self, brick_instance, on_termination_cb=lambda *args, **kwargs: None):
        self.uid = create_uid(prefix="R-")
        self.brick = brick_instance

        self.log = logging.TitanPlatformLogger(
            __name__, context=logging.FlowContext.from_brick(brick_instance)
        )

        self.process = None
        self.terminated = Flag()
        self.on_termination_cb = on_termination_cb

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if isinstance(other, BrickRunner):
            return other.uid == self.uid
        return False

    def __repr__(self):
        return f"BrickRunner(uid={self.uid}, brick={self.brick})"

    def start(self):
        """Start a new brick runner process"""

        br_command = [
            self.brick.base.exe,
            "-m",
            "titanfe.apps.brick_runner",
            "-id",
            str(self.uid),
            "-configuration",
            pickle.dumps(configuration).hex(),
            "-brick",
            pickle.dumps(self.brick).hex(),
        ]

        self.log.debug("command: %r", br_command)
        if os.name == "nt":
            self.process = subprocess.Popen(
                br_command,
                cwd=self.brick.base.venv_path,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,  # to allow SIGBREAK on windows
            )
        else:
            self.process = subprocess.Popen(br_command, cwd=self.brick.base.venv_path)

        br_exitcode = self.process.poll()
        if br_exitcode is not None:
            raise RuntimeError(f"Failed to start runner. ({br_exitcode})")

        asyncio.create_task(self.check_termination())

    async def check_termination(self):
        """
        do cyclic checks for an exitcode of the brick runner's process to detect it's termination
        """
        exitcode = None
        while exitcode is None:
            await asyncio.sleep(1)
            exitcode = self.process.poll()
        self.terminated.set()
        self.log.info("Runner terminated (%s) - %s", exitcode, self)
        self.on_termination_cb(self)

    async def stop(self):
        """request and await runner termination"""
        self.log.info("stop %r", self)

        if os.name == "nt":
            self.process.send_signal(signal.CTRL_BREAK_EVENT)  # pylint: disable=no-member
        else:
            self.process.send_signal(signal.SIGINT)

        try:
            await asyncio.wait_for(self.terminated.wait(), timeout=5)
        except asyncio.TimeoutError:
            self.log.with_context.warning("BrickRunner did not stop in a timely manner: %s", self)
