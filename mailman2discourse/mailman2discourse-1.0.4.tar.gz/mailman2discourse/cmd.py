import argparse
import logging
import sys
from mailman2discourse.importer import Importer

logging.basicConfig(format='%(funcName)s %(levelname)s %(message)s')


class Cmd(object):

    def __init__(self, *args):
        self.args = self.parser().parse_args(args)
        self.configure_logging()

    def configure_logging(self):
        logger = logging.getLogger('')
        logger.setLevel(logging.WARNING)

        logger = logging.getLogger('mailman2discourse')
        if self.args.debug:
            logger.setLevel(logging.DEBUG)
        elif self.args.verbose:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.WARNING)
        return logger.level

    def parser(self):
        parser = argparse.ArgumentParser(
            description="")

        parser.add_argument('--api-key',
                            help='Discourse api key',
                            required=True)
        parser.add_argument('--api-user',
                            help='Discourse api user',
                            default='api')
        parser.add_argument('--url',
                            help='Discourse URL',
                            required=True)
        parser.add_argument('--domain',
                            help='domain name of the mailing list',
                            required=True)
        parser.add_argument('--list',
                            help='name of the mailing list and the discourse category',
                            required=True)
        parser.add_argument('--mailman-config',
                            help='path to the config.pck file',
                            required=True)
        parser.add_argument('--mailman-encoding',
                            help='encoding of the config.pck file',
                            default='UTF-8')
        parser.add_argument('--force-private', action='store_const',
                            const=True,
                            help='all categories are created private regardless')
        parser.add_argument('--skip-ban-list', action='store_const',
                            const=True,
                            help='do not import the ban_list')
        parser.add_argument('--verbose', action='store_const',
                            const=True,
                            help='enable verbose logging')
        parser.add_argument('--debug', action='store_const',
                            const=True,
                            help='enable debug logging')
        parser.add_argument('--dry-run', action='store_const',
                            const=True,
                            help='display what would be done but do nothing')
        parser.add_argument('--preserve-existing-user-preferences', action='store_const',
                            const=True,
                            help=('do not set preferences for users that already exist '
                                  'when the import begins'))
        return parser

    def main(self):
        return Importer(self.args).main()


def main(argv=sys.argv[1:]):
    return Cmd(*argv).main()
