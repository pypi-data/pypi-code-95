#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cli entrypoint.
"""
import argparse

from . import __version__
from .package_info import command as package_info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-V", "--version", action="store_true", help="Print the codesee-util version number and exit")
    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands',
        help='codesee-py <subcommand> -h for subcommand help'
    )

    parser_package_info = subparsers.add_parser("package_info")
    parser_package_info.add_argument("directory", help="directory to search for Python package configuration files")
    parser_package_info.set_defaults(func=package_info)

    args = parser.parse_args()

    if (args.version):
        print(__version__)
        return

    try:
        args.func(args)
    except AttributeError:
        parser.print_help()
        raise Exception("codesee-py called without subcommand")


if __name__ == "__main__":
    main()
