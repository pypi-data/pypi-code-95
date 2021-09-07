from argparse import ArgumentParser
from . import log, base, graph, stat


def cli():
    # Construct all sub-commands under one main base command
    meed = base.Base(
        ArgumentParser(
            description="A configurable dialogue for tracking reoccurring mood stats"
        )
    )
    sub_parsers = meed.parser.add_subparsers(help="Moody subcommands")

    log.Log.sub_command(sub_parsers)
    graph.Graph.sub_command(sub_parsers)
    stat.Stat.sub_command(sub_parsers)

    meed.parse()

    return 0
