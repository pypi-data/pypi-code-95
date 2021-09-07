#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

""" Brick Runner (application)
"""

import argparse
import asyncio
import sys
from contextlib import suppress
from pathlib import Path
import os
import site

import titanfe.log
from titanfe.apps.control_peer.control_peer import ControlPeer
from titanfe.config import configuration

log = titanfe.log.getLogger(__name__)


async def run_app(args):
    """run the application"""
    configuration.update_from_yaml(args.config_file)
    configuration.brick_folder = Path(args.brick_folder).resolve()

    cp = ControlPeer.create()  # pylint: disable=invalid-name
    try:
        await cp.run()
    except KeyboardInterrupt:
        cp.schedule_shutdown("KeyboardInterrupt", None)


def main():
    """parse args and run the application"""
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        # TODO: deprecate
        "-brick_config",
        help="Brick configuration file",
        default="../../../examples/demo_flow.yml",
    )
    arg_parser.add_argument(
        "-brick_folder", help="Brick folder", default=str(Path.home() / "titanfe/bricks"),
    )
    arg_parser.add_argument(
        "-config_file",
        help="Location of the config file",
        default=Path(__file__).parent / "config.yaml",
    )
    args = arg_parser.parse_args()

    with suppress(asyncio.CancelledError):
        asyncio.run(run_app(args))


if __name__ == "__main__":
    if "win" in sys.platform:
        # see: https://docs.python.org/dev/whatsnew/3.8.html#asyncio
        # On Windows: Ctrl-C bug in asyncio (fixed in Py3.8) - TODO: workaround?
        # Windows specific event-loop policy (default in Py3.8)
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    else:
        import uvloop  # pylint: disable=import-error

        uvloop.install()

    # temporaly set PYTHONPATH to allow for not having to reinstall platform requirements
    # use all of current directory (to find brick runner module), user and global site packages
    os.environ["PYTHONPATH"] = "%s:%s:%s:%s" % (
        str(os.environ.get("PYTHONPATH") or ""),
        os.getcwd(),
        site.getusersitepackages(),
        ":".join(site.getsitepackages()),
    )
    main()
