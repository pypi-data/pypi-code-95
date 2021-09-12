import argparse
import sys

from .__version__ import ver
from .taskr import _Taskr

VERSION = ver


def main(args=None):
    parser = argparse.ArgumentParser(
        prog="taskr", description="A small utility to run tasks"
    )
    parser.add_argument(
        "-v", "--version", action="store_true", help="prints the version number"
    )
    parser.add_argument("-l", "--list", action="store_true", help="show defined tasks")
    parser.add_argument(
        "-i", "--init", action="store_true", help="generate a task file"
    )

    args, customs = parser.parse_known_args()

    if args.init:
        _Taskr.init()
        return

    if args.version:
        print(f"Running {VERSION}")
        return

    try:
        import tasks
    except ImportError:
        print("No valid tasks.py file found in current directory. Run 'taskr --init'")
        parser.print_help()
        sys.exit(1)

    T = _Taskr(tasks)

    # We really only want one value in customs for now
    # I'll add support for arguments later
    if customs:
        if len(customs) > 1:
            print("Error: More than 1 custom task passed")
            return
        custom = customs.pop()
        if custom.startswith("-"):
            parser.print_help()
        else:
            T.process(custom)
    elif len(sys.argv) > 1:
        if args.list:
            T.list()
    elif T.hasDefault():
        T.default()
    else:
        parser.print_help()
