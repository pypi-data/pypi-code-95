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
import pickle
import sys

from titanfe import log as logging
from titanfe.apps.brick_runner.runner import BrickRunner
from titanfe.config import configuration

if "win" in sys.platform:
    # Windows specific event-loop policy
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
else:
    import uvloop  # pylint: disable=import-error

    uvloop.install()


async def run_app(args):
    """ let's do this
    """

    configuration.update(pickle.loads(args.configuration))
    logging.initialize("BrickRunner")

    brick = pickle.loads(args.brick)

    runner = await BrickRunner.create(args.id, brick)
    try:
        await runner.run()
    except KeyboardInterrupt:
        runner.schedule_shutdown()


def main():

    """parse args and run the application"""
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-id", type=str, help="Brick Runner ID")  # uuid.UUID,
    arg_parser.add_argument("-configuration", type=bytes.fromhex, help="pickled configuration")
    arg_parser.add_argument("-brick", type=bytes.fromhex, help="pickled brick instance")

    args = arg_parser.parse_args()

    # asyncio.run(run_app(args))
    asyncio.get_event_loop().run_until_complete(run_app(args))


if __name__ == "__main__":
    main()
