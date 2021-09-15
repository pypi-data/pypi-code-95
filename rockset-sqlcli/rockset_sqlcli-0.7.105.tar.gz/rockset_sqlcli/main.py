# -*- coding: utf-8 -*-
import sys

from docopt import docopt
from rockset import version
from rockset_sqlcli.rscli.main import cli_main


def main(args=None):
    # init args from sys
    if args is None:
        args = sys.argv[1:]

    usage = """
SQL REPL for Rockset

Usage:
    rock-sql [-s=API_SERVER] API_KEY
    rock-sql --help
    rock-sql --version

Arguments:
    API_KEY                             api_key to authenticate to the Rockset API server

Options:
    --version                           display rockset version and exit
    -h, --help                          print help message and exit
    -s, --api_server=API_SERVER         address of the Rockset API server to connect to
                                        [default: api.rs2.usw2.rockset.com]
"""
    parsed_args = docopt(
        usage, argv=args, version=version(), options_first=True
    )

    return cli_main(
        api_server=parsed_args['--api_server'],
        api_key=parsed_args['API_KEY'],
        workspace='commons',
    )


if __name__ == '__main__':
    main()
