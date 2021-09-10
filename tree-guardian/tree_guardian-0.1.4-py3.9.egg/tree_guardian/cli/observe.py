#!/usr/bin/env python3

import sys
import argparse

from subprocess import check_call

from tree_guardian import observe, constants


def main():
    parser = argparse.ArgumentParser(description=observe.__doc__)
    parser.add_argument(
        '-d',
        '--debug',
        dest='debug',
        action='store_true',
        help='set debug log level'
    )
    parser.add_argument(
        '-c',
        '--callback',
        dest='callback',
        type=str,
        required=True,
        help='callback command'
    )
    parser.add_argument(
        '-p',
        '--path',
        dest='path',
        type=str,
        required=False,
        default='.',
        help='the observable root path'
    )
    parser.add_argument(
        '-e',
        '--exclude',
        dest='exclude',
        type=str,
        required=False,
        nargs='*',
        default=constants.EXCLUDE_RECOMMENDED,
        help='excluded files from observe'
    )
    args = parser.parse_args()

    if not args.debug:
        sys.stdout = open('/dev/null', 'w')

    def callback_command(cmd: str):
        check_call(cmd, shell=args.debug)

    observe(
        callback=callback_command,
        path=args.path,
        exclude=args.exclude,
        run_async=False
    )

    return 0


if __name__ == '__main__':
    sys.exit(main())
