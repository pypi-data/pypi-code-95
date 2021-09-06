# coding: utf-8
# flake8: noqa
# cligen: 0.1.5, dd: 2021-09-06

import argparse
import datetime
import importlib
import sys

from . import __version__


class CountAction(argparse.Action):
    """argparse action for counting up and down

    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action=CountAction, const=1,
            nargs=0)
    parser.add_argument('--quiet', '-q', action=CountAction, dest='verbose',
            const=-1, nargs=0)
    """

    def __call__(self, parser, namespace, values, option_string=None):
        if self.const is None:
            self.const = 1
        try:
            val = getattr(namespace, self.dest) + self.const
        except TypeError:  # probably None
            val = self.const
        setattr(namespace, self.dest, val)


class DateAction(argparse.Action):
    """argparse action for parsing dates with or without dashes

    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action=DateAction)
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs != 1 and nargs not in [None, '?', '*']:
            raise ValueError('DateAction can only have one argument')
        default = kwargs.get('default')
        if isinstance(default, str):
            kwargs['default'] = self.special(default)
        super(DateAction, self).__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        # this is only called if the option is specified
        if values is None:
            return None
        s = values
        for c in './-_':
            s = s.replace(c, '')
        try:
            val = datetime.datetime.strptime(s, '%Y%m%d').date()
        except ValueError:
            val = self.special(s)
        #    val = self.const
        setattr(namespace, self.dest, val)

    def special(self, date_s):
        if isinstance(date_s, str):
            today = datetime.date.today()
            one_day = datetime.timedelta(days=1)
            if date_s == 'today':
                return today
            if date_s == 'yesterday':
                return today - one_day
            if date_s == 'tomorrow':
                return today + one_day
            raise ValueError


def main(cmdarg=None):
    cmdarg = sys.argv if cmdarg is None else cmdarg
    parsers = []
    parsers.append(argparse.ArgumentParser(formatter_class=SmartFormatter))
    parsers[-1].add_argument('--verbose', '-v', nargs=0, dest='_gl_verbose', metavar='VERBOSE', default=0, help='D|increase verbosity level', action=CountAction)
    parsers[-1].add_argument('--dir', help='base directory for all downloads and extraction')
    parsers[-1].add_argument('--config', help='directory for config file', dest='_gl_config', metavar='CONFIG', default='~/.config/python_release_info/')
    parsers[-1].add_argument('--force', action='store_true', help='force download (and extraction), normally skipped if already there')
    parsers[-1].add_argument('--type', help='compiler type to work on: [cpython, tbd] (default: %(default)s)', dest='_gl_type', metavar='TYPE', default='cpython')
    parsers[-1].add_argument('--version', action='store_true', help='show program\'s version number and exit')
    subp = parsers[-1].add_subparsers()
    px = subp.add_parser('update', help='download release_info.pon to config directory (if --dir specified also download new versions)', formatter_class=SmartFormatter)
    px.set_defaults(subparser_func='update')
    parsers.append(px)
    parsers[-1].add_argument('--extract', help='extract newly downloaded versions', action='store_true')
    parsers[-1].add_argument('--build', '-b', help='newly extracted versions')
    parsers[-1].add_argument('--delay', help='delay updating for DELAY days', type=int)
    parsers[-1].add_argument('--verbose', '-v', nargs=0, help='D|increase verbosity level', action=CountAction)
    parsers[-1].add_argument('--dir', help='base directory for all downloads and extraction')
    parsers[-1].add_argument('--config', help='directory for config file')
    parsers[-1].add_argument('--force', action='store_true', help='force download (and extraction), normally skipped if already there')
    parsers[-1].add_argument('--type', help='compiler type to work on: [cpython, tbd] (default: %(default)s)')
    px = subp.add_parser('current', help='list of current major.minor.micro versions', formatter_class=SmartFormatter)
    px.set_defaults(subparser_func='current')
    parsers.append(px)
    parsers[-1].add_argument('--dd', action=DateAction, metavar='DATE', help='show versions current on %(metavar)s (default: %(default)s)')
    parsers[-1].add_argument('--verbose', '-v', nargs=0, help='D|increase verbosity level', action=CountAction)
    parsers[-1].add_argument('--dir', help='base directory for all downloads and extraction')
    parsers[-1].add_argument('--config', help='directory for config file')
    parsers[-1].add_argument('--force', action='store_true', help='force download (and extraction), normally skipped if already there')
    parsers[-1].add_argument('--type', help='compiler type to work on: [cpython, tbd] (default: %(default)s)')
    px = subp.add_parser('pre', help='list of not yet finalized releases', formatter_class=SmartFormatter)
    px.set_defaults(subparser_func='pre')
    parsers.append(px)
    parsers[-1].add_argument('--dd', action=DateAction, metavar='DATE', help='show versions current on %(metavar)s (default: %(default)s)')
    parsers[-1].add_argument('--verbose', '-v', nargs=0, help='D|increase verbosity level', action=CountAction)
    parsers[-1].add_argument('--dir', help='base directory for all downloads and extraction')
    parsers[-1].add_argument('--config', help='directory for config file')
    parsers[-1].add_argument('--force', action='store_true', help='force download (and extraction), normally skipped if already there')
    parsers[-1].add_argument('--type', help='compiler type to work on: [cpython, tbd] (default: %(default)s)')
    px = subp.add_parser('download', help='download/extract a particular version', formatter_class=SmartFormatter)
    px.set_defaults(subparser_func='download')
    parsers.append(px)
    parsers[-1].add_argument('--extract', action='store_true', help='extract downloaded tar file')
    parsers[-1].add_argument('version')
    parsers[-1].add_argument('--verbose', '-v', nargs=0, help='D|increase verbosity level', action=CountAction)
    parsers[-1].add_argument('--dir', help='base directory for all downloads and extraction')
    parsers[-1].add_argument('--config', help='directory for config file')
    parsers[-1].add_argument('--force', action='store_true', help='force download (and extraction), normally skipped if already there')
    parsers[-1].add_argument('--type', help='compiler type to work on: [cpython, tbd] (default: %(default)s)')
    parsers.pop()
    if '--version' in cmdarg[1:]:
        if '-v' in cmdarg[1:] or '--verbose' in cmdarg[1:]:
            return list_versions(pkg_name='release_info', version=None, pkgs=[])
        print(__version__)
        return
    args = parsers[0].parse_args(args=cmdarg[1:])
    for gl in ['verbose', 'config', 'type']:
        if getattr(args, gl, None) is None:
            setattr(args, gl, getattr(args, '_gl_' + gl))
        delattr(args, '_gl_' + gl)
    cls = getattr(importlib.import_module("release_info.release_info"), "ReleaseInfo")
    obj = cls(args)
    funcname = getattr(args, 'subparser_func', None)
    if funcname is None:
        parsers[0].parse_args('--help')
    fun = getattr(obj, args.subparser_func)
    return fun()


class SmartFormatter(argparse.HelpFormatter):
    """
    you can only specify one formatter in standard argparse, so you cannot
    both have pre-formatted description (RawDescriptionHelpFormatter)
    and ArgumentDefaultsHelpFormatter.
    The SmartFormatter has sensible defaults (RawDescriptionFormatter) and
    the individual help text can be marked ( help="R|" ) for
    variations in formatting.
    version string is formatted using _split_lines and preserves any
    line breaks in the version string.
    If one help string starts with D|, defaults will be added to those help
    lines that do not have %(default)s in them
    """

    _add_defaults = True  # make True parameter based on tag?

    def __init__(self, *args, **kw):
        super(SmartFormatter, self).__init__(*args, **kw)

    def _fill_text(self, text, width, indent):
        return ''.join([indent + line for line in text.splitlines(True)])

    def _split_lines(self, text, width):
        if text.startswith('D|'):
            SmartFormatter._add_defaults = True
            text = text[2:]
        elif text.startswith('*|'):
            text = text[2:]
        if text.startswith('R|'):
            return text[2:].splitlines()
        return argparse.HelpFormatter._split_lines(self, text, width)

    def _get_help_string(self, action):
        if SmartFormatter._add_defaults is None:
            return argparse.HelpFormatter._get_help_string(self, action)
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    help += ' (default: %(default)s)'
        return help

    def _expand_help(self, action):
        """mark a password help with '*|' at the start, so that
        when global default adding is activated (e.g. through a helpstring
        starting with 'D|') no password is show by default.
        Orginal marking used in repo cannot be used because of decorators.
        """
        hs = self._get_help_string(action)
        if hs.startswith('*|'):
            params = dict(vars(action), prog=self._prog)
            if params.get('default') is not None:
                # you can update params, this will change the default, but we
                # are printing help only after this
                params['default'] = '*' * len(params['default'])
            return self._get_help_string(action) % params
        return super(SmartFormatter, self)._expand_help(action)


def list_versions(pkg_name, version, pkgs):
    version_data = [
        ('Python', '{v.major}.{v.minor}.{v.micro}'.format(v=sys.version_info)),
        (pkg_name, __version__ if version is None else version),
    ]
    for pkg in pkgs:
        try:
            version_data.append((pkg,  getattr(importlib.import_module(pkg), '__version__', '--')))
        except ModuleNotFoundError:
            version_data.append((pkg, 'NA'))
        except KeyError:
            pass
    longest = max([len(x[0]) for x in version_data]) + 1
    for pkg, ver in version_data:
        print('{:{}s} {}'.format(pkg + ':', longest, ver))


if __name__ == '__main__':
    sys.exit(main())
