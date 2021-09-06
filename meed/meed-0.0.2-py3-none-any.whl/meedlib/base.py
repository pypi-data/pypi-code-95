import argparse
from argparse import ArgumentParser

from .config import MeedConfig
from .command import Command

__version__ = "0.0.2"


class Base(Command):
    def __init__(self, parser):
        Command.__init__(self, parser)

    def main(self, args: argparse.Namespace):
        config = MeedConfig()
        if args.list:
            config.terminal_list_profiles()
        if args.new:
            config.terminal_create_new_profile()

    def create(self):
        self.parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=__version__,
            help="Get the current meed version",
        )
        self.parser.add_argument(
            "-n",
            "--new",
            action="store_true",
            default=False,
            help="Setup a new meed profile",
        )
        self.parser.add_argument(
            "-l",
            "--list",
            action="store_true",
            default=False,
            help="Return a list of all meed profiles",
        )


if __name__ == "__main__":
    Base(
        ArgumentParser(
            description="A configurable dialogue for tracking reoccurring meed stats"
        )
    ).parse()
