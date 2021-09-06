#!python
from argparse import ArgumentParser
from meedlib import Log
from meedlib import Base
from meedlib import Graph
from meedlib import Stat


def main():
    # Construct all sub-commands under one main base command
    base = Base(
        ArgumentParser(
            description="A configurable dialogue for tracking reoccurring mood stats"
        )
    )
    sub_parsers = base.parser.add_subparsers(help="Moody subcommands")

    Log.sub_command(sub_parsers)
    Graph.sub_command(sub_parsers)
    Stat.sub_command(sub_parsers)

    base.parse()


if __name__ == "__main__":
    main()
