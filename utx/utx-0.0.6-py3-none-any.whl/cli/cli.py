#!/usr/bin/python
# encoding=utf-8

"""
@Author  :  Lijiawei
@Date    :  8/17/2021 6:49 PM
@Desc    :  Command line.
"""

import argparse
import sys

from utx import __description__, __version__
from utx.cli.scaffold import init_parser_scaffold, main_scaffold


def main():
    """Parse command line options and run commands.
    """
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument(
        "-v", "--version", dest="version", action="store_true", help="show version"
    )
    subparsers = parser.add_subparsers(help="sub-command help")
    sub_parser_scaffold = init_parser_scaffold(subparsers)

    if len(sys.argv) == 1:
        # utx
        parser.print_help()
        sys.exit(0)
    elif len(sys.argv) == 2:
        # print help for sub-commands
        if sys.argv[1] in ["-v", "--version"]:
            # utx -v
            print(f"{__version__}")
        elif sys.argv[1] in ["-h", "--help"]:
            # utx -h
            parser.print_help()
        elif sys.argv[1] == "startproject":
            # utx startproject
            sub_parser_scaffold.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.version:
        print(f"{__version__}")
        sys.exit(0)

    if sys.argv[1] == "startproject":
        main_scaffold(args)


def cli_env():
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument("--device", type=str)
    parser.add_argument("--platform", type=str)
    parser.add_argument("--wda", type=str)
    parser.add_argument("--init", type=str)
    args = parser.parse_args()
    cli_device = args.device
    cli_platform = args.platform
    cli_wda = args.wda
    cli_init = args.init

    return cli_device, cli_platform, cli_wda, cli_init
