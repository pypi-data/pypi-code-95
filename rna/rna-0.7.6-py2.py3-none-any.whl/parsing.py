"""
Collection of generic parent parsers
"""
import argparse
import logging


# pylint:disable=protected-access
class LoggingAction(argparse._StoreAction):
    """
    Call basic config with namespace.level
    """

    def __call__(self, parser, namespace, values, option_string=None):
        super().__call__(parser, namespace, values, option_string=option_string)
        logging.basicConfig(level=namespace.level)


class LogParser(argparse.ArgumentParser):
    """
    Parent parser with the "level" argument, automatically setting the logging level
    """

    def __init__(self, add_help=False, **kwargs):
        super().__init__(add_help=add_help, **kwargs)
        self.add_argument(
            "--level",
            "-l",
            type=int,
            default=logging.INFO,
            help="Logger level",
            action=LoggingAction,
        )
