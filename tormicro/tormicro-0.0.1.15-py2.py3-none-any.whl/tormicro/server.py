# Copyright (c) 2020. All rights reserved.
import json

import aiotask_context as context  # type: ignore
import argparse
import asyncio
import logging
import logging.config
import yaml
import os
import sys

import tornado.web

# from tormicro import LOGGER_NAME
from tormicro import AppContext
from tormicro.app import make_tormicro_app
import tormicro.utils.logutils as logutils
from tormicro.config import ConfigDict, load_config_local
from tormicro.utils import modutils


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='Run Address Book Server'
    )

    parser.add_argument(
        '-p',
        '--port',
        type=int,
        # default=8080,
        help='port number for %(prog)s server to listen; '
             'default: %(default)s'
    )

    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='turn on debug logging'
    )

    parser.add_argument(
        '-c',
        '--config',
        # required=True,
        type=argparse.FileType('r'),
        help='config file for %(prog)s'
    )

    parser.add_argument(
        '-w',
        '--workdir',
        default='.',
        type=str,
        help='work directory to start %(prog)s server, defaults to "."'
    )

    parser.add_argument(
        '-e',
        '--env',
        default='local',
        type=str,
        help='work environment to start %(prog)s server, defaults to "local"'
    )

    parser.add_argument(
        '-v',
        '--version',
        default='Latest',
        type=str,
        help='the service version'
    )

    args = parser.parse_args(args)
    return args


def run_server(
        app: tornado.web.Application,
        config: ConfigDict,
        port: int,
        debug: bool,
        logger: logging.Logger
):
    name = config.application.name
    loop = asyncio.get_event_loop()
    loop.set_task_factory(context.task_factory)

    # Bind http server to port
    http_server_args = {
        'decompress_request': True
    }
    http_server = app.listen(port, '', **http_server_args)
    logutils.log(
        logger,
        logging.INFO,
        message=f'Service {name} is STARTING',
        service=name,
        port=port
    )

    try:
        # Start asyncio IO event loop
        loop.run_forever()
    except KeyboardInterrupt:
        # signal.SIGINT
        pass
    finally:
        loop.stop()
        logutils.log(
            logger,
            logging.INFO,
            message='SHUTTING DOWN',
            service_name=name
        )
        http_server.stop()
        # loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
        loop.run_until_complete(loop.shutdown_asyncgens())

        AppContext.stop()

        loop.close()
        logutils.log(
            logger,
            logging.INFO,
            message='STOPPED',
            service_name=name
        )


def init_workdir(
        workdir: str
) -> str:
    workdir_path = os.path.abspath(workdir)
    if workdir_path not in sys.path:
        sys.path.append(workdir_path)

    default_bootstrap_files = ['bootstrap.yaml', 'bootstrap.yml']
    for default_bootstrap_file in default_bootstrap_files:
        bootstrap_file = os.path.join(workdir_path, default_bootstrap_file)
        if os.path.exists(bootstrap_file):
            return bootstrap_file

    return None


def main(args=parse_args()) -> None:
    """
    Starts the Tornado server on the given port
    """
    bootstrap_file: str = init_workdir(args.workdir)

    with bootstrap_file and open(bootstrap_file, 'r') as bf:
        bootstrap = ConfigDict(yaml.load(bf, Loader=yaml.SafeLoader))

    config = None
    if bootstrap:
        config = load_config_local(bootstrap, args.env, args.workdir)
        if bootstrap.config.loader:
            ext_config_loader = modutils.load_object(str(bootstrap.config.loader))
            ext_config = ext_config_loader(bootstrap, args.env, args.workdir)
            config = config.merge(ext_config)
    elif args.config:
        config = ConfigDict(yaml.load(args.config.read(), Loader=yaml.SafeLoader))

    assert config, 'the configuration of tormicro app is not properly initialized'

    config.application.version = args.version
    config.env = args.env
    if config.application.version == 'Latest':
        config.application.version = os.getenv('APP_VERSION', 'Latest')

    # First thing: set logging config
    logging.config.dictConfig(config.logging.to_dict())
    logger = logging.getLogger(config.application.name)

    addr_app = make_tormicro_app(config, args.debug, logger)

    logutils.log(logger, logging.INFO,
                 message=f'Starting tormicro app {config.application.name}, version={config.application.version},'
                         f'bootstrap={bootstrap.to_dict()}')

    run_server(
        app=addr_app,
        config=config,
        port=args.port or config.server.port,
        debug=args.debug,
        logger=logger
    )


if __name__ == '__main__':
    main()
