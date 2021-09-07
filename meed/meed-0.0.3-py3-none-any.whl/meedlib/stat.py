import argparse
from csv import reader

from .config import MeedConfig, MeedConfigNotExists
from .terminal import fatal_error
from .command import Command


class Stat(Command):
    def __init__(self, parser):
        Command.__init__(self, parser)

    def main(self, args: argparse.Namespace):
        if not args.log:
            return
        try:
            config = MeedConfig(args.log)
            relevant_stats = []
            with open(config["Output_File"]) as file:
                csv_reader = reader(file)
                for row in csv_reader:
                    profile, datetime, stats = row[0], row[1], row[2:]
                    if profile != args.log:
                        continue
                    relevant_stats.append([int(i) for i in stats])
            print(relevant_stats)
        except MeedConfigNotExists:
            fatal_error(MeedConfigNotExists.MESSAGE)
        except FileNotFoundError:
            fatal_error(
                f"Could not find output file, check your configuration"
            )

    def create(self):
        self.parser.add_argument(
            "log",
            help="Name of the meed log profile",
        )
        self.parser.add_argument(
            "--start_time",
            help="Number of days to calculate stats back to",
        )
        self.parser.add_argument(
            "--end_time",
            help="Number of days to calculate stats back to",
        )


if __name__ == "__main__":
    Stat(argparse.ArgumentParser()).parse()
