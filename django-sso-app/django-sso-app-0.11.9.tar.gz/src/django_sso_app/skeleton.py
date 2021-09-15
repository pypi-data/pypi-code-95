# -*- coding: utf-8 -*-
"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
[options.entry_points] section in setup.cfg:

    console_scripts =
         fibonacci = django_sso_app.skeleton:run

Then run `python setup.py install` which will install the command `fibonacci`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.

Note: This skeleton file can be safely removed if not needed!
"""

import argparse
import os
import sys
import logging

from django_sso_app import __version__
import server

__author__ = "pai"
__copyright__ = "pai"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def call_django():
    django_settings_module = os.environ.get('DJANGO_SETTINGS_MODULE',
                                            'django_sso_app.config.settings.local')
    _logger.info("DJANGO_SETTINGS_MODULE: {}".format(django_settings_module))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', django_settings_module)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv[1:])


def run_server():
    server.run()


def parse_args(parser, args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """

    parser.add_argument(
        "--version",
        action="version",
        version="django-sso-app {ver}".format(ver=__version__))

    parser.add_argument(
        dest="ctx",
        help="The command context")

    parser.add_argument(
        dest="cmd",
        help="The command")

    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO)

    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG)

    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """

    parser = argparse.ArgumentParser(description="Django SSO App")

    args = parse_args(parser, args)

    setup_logging(args.loglevel)

    ctx = args.ctx
    cmd = args.cmd

    _logger.debug("Context: {}".format(ctx))

    if ctx == 'django':
        print('running manage.py {}'.format(cmd))
        call_django()

    if ctx == 'server':
        if cmd =='run':
            print('running server.py ({})'.format(cmd))
            run_server()
        else:
            print('Undefined command: ({})'.format(cmd))

    _logger.info("Script ended")


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
