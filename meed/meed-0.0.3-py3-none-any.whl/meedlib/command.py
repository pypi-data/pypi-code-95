from argparse import ArgumentParser


class Command:
    def __init__(self, base: ArgumentParser):
        self.parser = base
        self.parser.set_defaults(func=self.main)
        self.create()

    def main(self, args):
        raise NotImplementedError

    def create(self):
        raise NotImplementedError

    def parse(self):
        args = self.parser.parse_args()
        args.func(args)

    @classmethod
    def sub_command(cls, base: "_SubParsersAction") -> "Command":
        parser = base.add_parser(cls.__name__.lower())
        return cls(parser)
