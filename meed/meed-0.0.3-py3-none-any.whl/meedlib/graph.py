import argparse

from .command import Command


class Graph(Command):
    def __init__(self, parser):
        Command.__init__(self, parser)

    def main(self, args: argparse.Namespace):
        pass

    def create(self):
        pass


if __name__ == "__main__":
    Graph(argparse.ArgumentParser()).parse()
