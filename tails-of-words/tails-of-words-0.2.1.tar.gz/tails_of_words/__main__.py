import logging
import json
import yaml

from . import __version__ as VERSION
from .__config__ import score_config
from .__words__ import Words
from .__swing__ import Swing, SwingOption
from .__swing__ import Section
from argparse import ArgumentParser
from argparse import FileType

LOG_LEVEL = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL']
USER_CHOICE = LOG_LEVEL+list(map(lambda w: w.lower(), LOG_LEVEL))
TYPE_CHOICE = ['csv', 'xml', 'html', 'plain']


class Process:

    def __init__(self, args):
        self.logger = logging.getLogger(__name__)
        self.ids = [6, 15]
        self.args = args
        if len(args.hinsi):
            self.ids = []
            for x in args.hinsi:
                for id in x.split(','):
                    self.ids.append(int(id))
        self.words = self.get_words(args.sources, args.exclude, args.column, args.html2text, args.stdin_type)
        self.logger.debug(vars(score_config))

    def get_words(self, sources, excludes, column, is_html2text, stdin_type):
        words = Words(excludes, column, is_html2text, stdin_type)
        for src in sources:
            words.parse(src)
        return words

    def get_hinsi(self):
        d = {}
        for id in self.ids:
            if id in self.words.hinsi:
                d[id] = sorted(self.words.hinsi[id].items(), key=lambda x:len(x[1]))
        return d

    def _swing(self):
        option = SwingOption(
            self.args.exclude_alphabet,
            self.args.exclude_ascii,
            self.args.jaro_winkler)
        return Swing(option)

    def get_distance(self):
        for x in self._swing().distance(self.words, self.ids):
            for d in x:
                yield d

    def get_swing(self, num, threshold):
        if num > 0:
            high = []
            for x in self._swing().swing(self.words, self.ids):
                tx = list(filter(lambda x:x.score >= threshold, x))
                high.extend(tx[0:num])
                high = sorted(high, reverse=True, key=lambda x: x.score)[0:num]
            for d in high:
                yield d
        else:
            for x in self._swing().swing(self.words, self.ids):
                for d in x:
                    yield d


class JsonWritter:

    def __init__(self, output, encoding="utf-8"):
        self.output = None
        self.obj = {}
        if output:
            self.output = open(output, 'w', encoding=encoding)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.output:
            self.output.close()

    def add(self, obj):
        if self.output:
            if isinstance(obj, Section):
                if 'sections' not in self.obj:
                    self.obj['sections'] = []
                self.obj['sections'].append({
                    "vs": "{}vs{}".format(obj.a.midasi, obj.b.midasi),
                    "distance": {
                        "levenshtein": obj.distance.levenshtein.__dict__,
                        "normalized": obj.distance.normalized.__dict__,
                        "jaro_winkler": obj.distance.jaro_winkler.__dict__
                    },
                    "score": obj.score,
                    "mrphs": [obj.a.get_rep_mrph_dict(), obj.b.get_rep_mrph_dict()],
                })
            elif isinstance(obj, tuple):
                self.obj[obj[0]] = obj[1]

    def dump(self):
        if self.output:
            # print(json.dumps(self.obj, indent=4, ensure_ascii=False))
            json.dump(self.obj, self.output, indent=4, ensure_ascii=False)


class CLI:

    def __init__(self):
        self.setup()

    def setup(self):
        self.parser = ArgumentParser()
        self.parser.add_argument(
            '-v',
            '--version',
            action='version',
            version=u'%(prog)s version ' + VERSION
        )
        self.parser.add_argument(
            '--dumpversion',
            action='version',
            version=VERSION
        )
        self.parser.add_argument(
            '--log',
            choices=USER_CHOICE,
            default="WARN",
            help="set log level"
        )
        self.parser.add_argument(
            '-c',
            '--config',
            type=FileType("r"),
            help="config.yml file path"
        )
        self.parser.add_argument(
            '-f',
            '--stdin-type',
            '--stdin-format',
            dest='stdin_type',
            choices=TYPE_CHOICE,
            default="",
            help="set stdin format type"
        )
        self.parser.add_argument(
            '--h2t',
            '--html2text',
            dest='html2text',
            action='store_true',
            help="Convert input text with html2text"
        )

        subparser = self.parser.add_subparsers()

        count_cmd = subparser.add_parser(
            'count',
            description='count words',
            help='count words. see `count -h`')
        count_cmd.set_defaults(handler=self.command_count)

        distance_cmd = subparser.add_parser(
            'distance',
            description='distance counted words',
            help='distance counted words. see `distance -h`')
        distance_cmd.set_defaults(handler=self.command_distance)

        show_cmd = subparser.add_parser(
            'show',
            description='show words',
            help='show words. see `show -h`')
        show_cmd.set_defaults(handler=self.command_show)
        show_cmd.add_argument(
            '-a',
            '--attr',
            action='append',
            default=[],
            help="set show mrph attributes"
        )

        swing_cmd = subparser.add_parser(
            'swing',
            description='show notation fluctuations',
            help='show notation fluctuations. see `swing -h`')
        swing_cmd.set_defaults(handler=self.command_swing)
        swing_cmd.add_argument(
            '-n',
            '--num',
            type=int,
            default=30,
            help="Display n items from the highest score. All if n is less than or equal to 0"
        )
        swing_cmd.add_argument(
            '-t',
            '--threshold',
            type=float,
            default=0.0,
            help="Display words whose score exceeds the threshold."
        )

        distance_cmds = [distance_cmd, swing_cmd]
        for cmd in distance_cmds:
            cmd.add_argument(
                '--jw',
                '--jaro-winkler',
                dest='jaro_winkler',
                action='store_true',
                help="use jaro_winkler."
            )
            cmd.add_argument(
                '--no-alnum',
                '--exclude-alphabet',
                dest='exclude_alphabet',
                action='store_true',
                help="exclude isalpha or isalnum string."
            )
            cmd.add_argument(
                '--no-ascii',
                '--exclude-ascii',
                dest='exclude_ascii',
                action='store_true',
                help="exclude isascii string."
            )

        input_file_cmds = [count_cmd, distance_cmd, show_cmd, swing_cmd]
        for cmd in input_file_cmds:
            cmd.add_argument(
                '-o',
                '--output',
                help="output json file path."
            )
            cmd.add_argument(
                '-c',
                '--column',
                action='append',
                default=[],
                help="specific csv file column name."
            )
            cmd.add_argument(
                '-i',
                '--hinsi',
                action='append',
                default=[],
                help="set collect hinsi_id. default [6, 15]"
            )
            cmd.add_argument(
                '-e',
                '--exclude',
                action='append',
                default=[],
                help="exclude files"
            )
            cmd.add_argument(
                'sources',
                metavar='SOURCE',
                nargs='+',
                help='input files'
            )

        subcommands = self.parser.format_usage().split('{')[1].split('}')[0]
        help_cmd = subparser.add_parser('help', help='show subcommand help. see `help -h`')
        help_cmd.set_defaults(handler=self.command_help)
        help_cmd.add_argument(
            'subcommand',
            nargs=1,
            help='subcommand name {' + subcommands + '}'
        )
        help_cmd_default_usage = help_cmd.format_usage().replace('usage: ', '')
        help_cmd.usage = help_cmd_default_usage.replace('subcommand', 'subcommand{' + subcommands + '}')

    def parse_command_line(self, argv):
        args = self.parser.parse_args(argv)
        if args.config:
            config = yaml.safe_load(args.config)
            for k, v in config.items():
                if k in args:
                    setattr(args, k, v)
                elif k == "score_config":
                    for sk, sv in v.items():
                        setattr(score_config, sk, sv)
        numeric_level = getattr(logging, args.log.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % args.log)
        logging.basicConfig(level=numeric_level)
        return args

    def get_process(self, args):
        return Process(args)

    def command_count(self, args):
        proc = self.get_process(args)
        with JsonWritter(args.output) as jw:
            for v in proc.get_hinsi().values():
                for word, arr in v:
                    print("{} : {}".format(len(arr), word))
                    jw.add((word, len(arr)))
            jw.dump()

    def command_distance(self, args):
        proc = self.get_process(args)
        with JsonWritter(args.output) as jw:
            for d in proc.get_distance():
                jw.add(d)
                print(d.format())
            jw.dump()

    def command_swing(self, args):
        proc = self.get_process(args)
        with JsonWritter(args.output) as jw:
            for d in proc.get_swing(args.num, args.threshold):
                jw.add(d)
                print(d.format())
            jw.dump()

    def get_variables(self, mrph, vars):
        s = []
        for v in vars:
            id = v + "_id"
            if hasattr(mrph, v):
                if hasattr(mrph, id):
                    s.append("{}({})".format(getattr(mrph, v), getattr(mrph, id)))
                else:
                    s.append("{}".format(getattr(mrph, v)))
        return s

    def command_show(self, args):
        proc = self.get_process(args)
        vars = args.attr
        if len(vars) == 0:
            vars.append('hinsi')
        for mrphs in proc.words.mrphs:
            infos = []
            s = ""
            prev = ""
            for mrph in mrphs:
                infos.insert(0, "{}└ {}".format(prev, ','.join(self.get_variables(mrph, vars))))
                prev = "\033[34m{}\033[33m\033[4m{}\033[0m".format(s, mrph.midasi)
                s += mrph.midasi
            print(prev)
            for info in infos:
                print(info)

    def command_help(self, args):
        print(self.parser.parse_args([args.subcommand[0], '--help']))

    def print_help(self):
        self.parser.print_help()

    def execute(self):
        self.execute_with_args()

    def execute_with_args(self, argv=None):
        args = self.parse_command_line(argv)
        if hasattr(args, 'handler'):
            args.handler(args)
        else:
            self.print_help()

def main():
    cli = CLI()
    cli.execute()

if __name__ == '__main__':
    main()
