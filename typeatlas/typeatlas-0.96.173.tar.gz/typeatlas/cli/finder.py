# -*- coding: utf-8 -*-
#
#    TypeAtlas CLI Finder Functions
#    Copyright (C) 2018-2021 Milko Krachounov
#
#    This file is part of TypeAtlas
#
#    TypeAtlas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    TypeAtlas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TypeAtlas.  If not, see <http://www.gnu.org/licenses/>.
#
#                                 ***
#
#    Alternatively, you may use this file (part of TypeAtlas command-line)
#    under the terms of the X11/MIT license as follows:
#
#    Permission is hereby granted, free of charge, to any person
#    obtaining a copy of this software and associated documentation
#    files (the "Software"), to deal in the Software without
#    restriction, including without limitation the rights to use,
#    copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following
#    conditions:
#
#    The above copyright notice and this permission notice shall be
#    included in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#    OTHER DEALINGS IN THE SOFTWARE.
#

from __future__ import division

import re
import os
import sys
import glob
import fnmatch
import argparse
import operator
import shutil

from itertools import groupby, chain
from operator import attrgetter
from typeatlas import fontlist, filtering
from typeatlas.langutil import _, N_, textlang
from typeatlas.util import isatty, tty_clear


FAMILY_PRINT_FORMAT = '{family}\n'
STYLE_PRINT_FORMAT = '{family} {style}\n'
FILE_PRINT_FORMAT = '{file}\n'


AUTO = object()


find_argparser = argparse.ArgumentParser(_('TypeAtlas font finder'))

matcher_dests = set()
matcher_factories = {}


comparisons = {
    # Readable operators
    '=': operator.eq,
    '!=': operator.ne,
    '!': operator.ne,
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,

    # Shell-safe operators, similar to find
    '++': operator.gt,
    '--': operator.lt,
    '+': operator.ge,
    '-': operator.le,

}


def split_comparison(arg):

    for op, func in comparisons.items():
        if arg.startswith(op):
            return func, arg[len(op):]

    return None, arg


opening_bracket = frozenset('{([')
closing_bracket = frozenset('})]')
matching_bracket = dict(['{}', '()', '[]', '}{', ')(', ']['])


class ParseError(ValueError):
    pass


def parse_expression(args):

    """Parse a font matching expression using the defined predicates"""

    return _parse_expression_lowlevel(args)[1]


def _parse_expression_lowlevel(args, i=0, expect_bracket=None, single=False):

    """Parse a font matching expression using the defined predicates
    that starts at the given index. If a paren is open, pass the closing
    paren in expect_bracket."""

    CONJ = object()

    got_paren = False

    predicate_group = []
    predicate_groups = [predicate_group]

    while i < len(args):
        arg = args[i]

        if arg in closing_bracket:
            if arg != expect_bracket:
                raise ParseError(_("Unexpected %r") % (arg, ))
            got_paren = True
            i += 1
            break

        elif arg in opening_bracket:
            i, matcher = _parse_expression_lowlevel(args, i + 1,
                                                    matching_bracket[arg])
            predicate_group.append(matcher)
            continue

        elif arg == 'or':
            predicate_group = []
            predicate_groups.append(predicate_group)

        elif arg == 'and':
            pass

        elif arg == 'not':
            i, matcher = _parse_expression_lowlevel(args, i + 1, single=True)
            predicate_group.append(Negation(matcher))
            continue

        else:
            try:
                matcher_cls = matcher_factories[arg]

            except KeyError:
                raise ParseError(_("Invalid predicate %r") % (arg, ))

            else:
                if len(args) < i + matcher_cls.nargs + 1:
                    raise ParseError("Missing arguments")
                matcher_args = args[i + 1:i + matcher_cls.nargs + 1]
                i += matcher_cls.nargs
                predicate_group.append(matcher_cls(*matcher_args))

        i += 1

        if single:
            break

    if expect_bracket and not got_paren:
        raise ParseError(_("Missing %s") % (expect_bracket, ))

    if not all(predicate_groups):
        raise ParseError(_("Empty expression"))

    return i, Disjunction.make(map(Conjunction.make, predicate_groups))



def add_matcher(*options, disjunctive_group=None, nargs=None, **kwargs):

    """Register a matcher as an option and an expression predicate."""

    def decorator(cls):
        if nargs == 0:
            const = cls()
            action = 'append_const'
        else:
            const = None
            action = 'append'
            kwargs.update(type=cls)
            if nargs is not None:
                kwargs.update(nargs=nargs)

        arg = find_argparser.add_argument(*options,
                                          action=action,
                                          const=const,
                                          **kwargs)
        cls.argspec = arg
        cls.disjunctive_group = disjunctive_group
        cls.nargs = 1
        if arg.nargs is not None:
            if not isinstance(arg.nargs, int):
                raise TypeError("nargs must be integer")
            cls.nargs = arg.nargs

        matcher_dests.add(arg.dest)
        matcher_factories[arg.dest] = cls
        return cls

    return decorator


def get_matchers(args):

    expression = args.expression
    if expression:
        yield parse_expression(expression)

    for dest in matcher_dests:
        matchers = getattr(args, dest) or ()
        for matcher in matchers:
            matcher.set_args(args)
            yield matcher


class Matcher(object):
    """Base for classes that match/select fonts."""

    disjunctive_group = None
    uses_extended = False
    slow = False
    args = None

    def __init__(self, arg):
        self.arg = arg

    def set_args(self, args):
        self.args = args

    def match(self, font):
        return True

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.arg)


class Conjunction(Matcher):

    """A conjunction ("and") of matchers"""

    def __init__(self, matchers):
        self.matchers = matchers

    @classmethod
    def make(cls, matchers):
        matchers = list(matchers)
        if len(matchers) == 1:
            return matchers[0]
        return cls(matchers)

    def set_args(self, args):
        for matcher in self.matchers:
            matcher.set_args(args)
        self.slow = any(matcher.slow for matcher in self.matchers)
        self.uses_extended = any(matcher.uses_extended
                                 for matcher in self.matchers)

    def match(self, font):
        return all(matcher.match(font) for matcher in self.matchers)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.matchers)


class Disjunction(Matcher):

    """A conjunction ("or") of matchers"""

    def __init__(self, matchers):
        self.matchers = matchers

    @classmethod
    def make(cls, matchers):
        matchers = list(matchers)
        if len(matchers) == 1:
            return matchers[0]
        return cls(matchers)

    def set_args(self, args):
        for matcher in self.matchers:
            matcher.set_args(args)
        self.slow = any(matcher.slow for matcher in self.matchers)
        self.uses_extended = any(matcher.uses_extended
                                 for matcher in self.matchers)

    def match(self, font):
        return any(matcher.match(font) for matcher in self.matchers)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.matchers)


class Negation(Matcher):

    """A negation ("not") of matchers"""

    def __init__(self, matcher):
        self.matcher = matcher

    def set_args(self, args):
        self.matcher.set_args(args)
        self.slow = self.matcher.slow
        self.uses_extended = self.matcher.uses_extended

    def match(self, font):
        return not self.matcher.match(font)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.matcher)


def _make_name_matcher(cat, prefix, opt, multi, langs, extended,
                       regex, casesensitive):

    """Create a name matcher for the given category, using the given prefix
    prepended to the name, with the given short option.

    multi is True if fontlist.Font supports multiple arguments here,
    langs is True if it supports localization, extended if it is gotten from
    the extended info, regex is True if we should create regex match, and
    casesensitive is True if we want to create a case sensitive matcher.

    The lowercase category with spaces replaced with underscores is the
    attribute used to get the property.]
    """

    if regex:
        name = cat.capitalize() + 'Regex'
        help = _('Select fonts whose %s matches a regular expression') \
                    % (_(cat), )
    else:
        name = cat.capitalize() + 'Name'
        help = _('Select fonts whose %s contains a string or wildcard pattern. '
                 'Prefix with = to to get exact match, or with ~ to '
                 'match the pattern against the whole name.') \
                    % (_(cat), )

    attr = name.lower().replace(' ', '_')

    if regex:
        flags = '(?ms)' if casesensitive else '(?ims)'
    else:
        flags = '' if casesensitive else '(?i)'

    if regex:
        option = '--' + prefix + '-regex' if prefix else '--regex'
    else:
        option = '--' + prefix if prefix else '--name'

    if casesensitive:
        name += 'Case'
        help += '; ' + _('Use case sensitive matching.')
        option += '-case'

    options = (option, )
    if opt:
        options += (opt, )

    @add_matcher(*options, disjunctive_group=cat, help=help,
                           metavar=_('PATTERN'))
    class NameMatcher(Matcher):

        uses_extended = extended

        def __init__(self, pattern):
            self.arg = pattern
            if not regex:
                if pattern.startswith('='):
                    pattern = '^' + re.escape(pattern[1:]) + '$'
                elif pattern.startswith('~'):
                    pattern = fnmatch.translate(pattern)
                else:
                    pattern = fnmatch.translate('*' + pattern + '*')
            self.regex = re.compile(flags + pattern)

        def match(self, font):
            if extended:
                font = font.extended()

            attr = cat

            if multi:
                attr += '_alts'
            if langs:
                attr += '_by_lang'

            if langs:
                names = getattr(font, attr).values()
            else:
                names = getattr(font, attr)

            if multi:
                names = chain.from_iterable(names)
            else:
                names = (names, )

            return any(v is not None and self.regex.search(v)
                       for v in names)


def _make_name_matchers():
    """Create all the name matchers"""

    for cat, prefix, o, oci, orx, orxci, multi, langs, ext in [
        (N_('family'), '', '-n', '-N', '-x', '-X', True, True, False),
        (N_('style'), 'style', '-s', '-S', '', '', True, True, False),
        (N_('fullname'), 'fullname', '', '', '', '', True, True, False),
        (N_('file'), 'filename', '-f', '-F', '', '', False, False, False),
        (N_('foundry'), 'foundry', '', '', '', '', False, False, False),

        (N_('description'), 'description', '', '', '', '', False, False, True),
        (N_('copyright'), 'copyright', '', '', '', '', False, False, True),
        (N_('trademark'), 'trademark', '', '', '', '', False, False, True),
        (N_('license'), 'license', '', '', '', '', False, False, True),
        (N_('license URL'), 'license-url', '', '', '', '', False, False, True),
        (N_('designer'), 'designer', '', '', '', '', False, False, True),
        (N_('manufacturer'), 'manufacturer', '', '', '', '',
         False, False, True),
        (N_('vendor URL'), 'vendor-url', '', '', '', '', False, False, True),
        (N_('designer URL'), 'designer-url', '', '', '', '', False, False, True),
        (N_('sample text'), 'sample-text', '', '', '', '', False, False, True),
        (N_('version'), 'version', '', '', '', '', False, False, True),

    ]:

        _make_name_matcher(cat, prefix, o, multi, langs, ext, False, False)
        _make_name_matcher(cat, prefix, oci, multi, langs, ext, False, True)
        _make_name_matcher(cat, prefix, orx, multi, langs, ext, True, False)
        _make_name_matcher(cat, prefix, orxci, multi, langs, ext, True, True)


_make_name_matchers()


def get_character_matcher(characters, qt=AUTO, contains_all=True):

    """Return an unary function that returns True if a font passed to it
    contains the given characters. If you pass qt=True, the function will
    use Qt functions, if you pass qt=False it will use typeatlas. By
    default it attempts to use Qt and fallbacks to typeatlas."""

    require = all if contains_all else any

    characters = set(map(ord, characters))

    if qt is AUTO:

        qt = False

        #if 'DISPLAY' in os.environ:
        #    try:
        #        from typeatlas.compat import QtGui
        #    except ImportError:
        #        pass
        #    else:
        #        qt = hasattr(QtGui, 'QRawFont')

    if qt:
        from typeatlas.compat import QtGui
        fontdb = QtGui.QFontDatabase()

        def character_matcher(font):
            import gc
            gc.collect()
            qfont = fontdb.font(font.family, font.family, 16)
            supports_char = QtGui.QRawFont.fromFont(qfont).supportsCharacter
            if not require(supports_char(c) for c in characters):
                return False
            return True

        character_matcher.uses_extended = False

    elif fontlist.FontFinder.supported():

        def character_matcher(font):
            charrange = font.charset
            if not require((c in charrange) for c in characters):
                return False
            return True

        character_matcher.uses_extended = False

    else:
        def character_matcher(font):
            extended = font.extended()
            if extended is not None and extended.cmap:
                cmap = extended.cmap
                if not require((c in cmap) for c in characters):
                    return False
            else:
                return False

            return True

        character_matcher.uses_extended = True

    return character_matcher


@add_matcher('--weight', '-W', help=_("Font weight, e.g. 'bold', '>=120'"))
class Weight(Matcher):

    def __init__(self, arg):
        self.arg = arg
        comp, value = split_comparison(arg)
        if value == 'bold':
            comp = operator.gt
            value = (fontlist.WEIGHT_BOLD + fontlist.WEIGHT_NORMAL) / 2
        elif value == 'regular':
            comp = lambda val, valrange: valrange[0] < val <= valrange[0]
            value = ((fontlist.WEIGHT_NORMAL + fontlist.WEIGHT_LIGHT) / 2,
                     (fontlist.WEIGHT_BOLD + fontlist.WEIGHT_NORMAL) / 2)
        elif value == 'light':
            comp = operator.le
            value = (fontlist.WEIGHT_NORMAL + fontlist.WEIGHT_LIGHT) / 2

        else:
            value = float(value)

        self.comp = comp
        self.value = value

    def match(self, font):
        return self.comp(font.weight, self.value)


@add_matcher('--slant', '-I', help=_("Font slant, e.g. 'italic', '>=30'"))
class Slant(Matcher):


    def __init__(self, arg):
        self.arg = arg
        comp, value = split_comparison(arg)
        if value == 'oblique':
            comp = operator.gt
            value = (fontlist.SLANT_OBLIQUE + fontlist.SLANT_ITALIC) / 2
        elif value == 'italic':
            comp = operator.gt
            value = (fontlist.SLANT_ITALIC + fontlist.SLANT_NORMAL) / 2
        elif value == 'regular':
            comp = operator.le
            value = (fontlist.SLANT_ITALIC + fontlist.SLANT_NORMAL) / 2
        else:
            value = float(value)

        self.comp = comp
        self.value = value

    def match(self, font):
        return self.comp(font.slant, self.value)


@add_matcher('--width', help=_("Font slant, e.g. 'condensed', '<=70'"))
class Width(Matcher):


    def __init__(self, arg):
        self.arg = arg
        comp, value = split_comparison(arg)
        if value == 'condensed':
            comp = operator.le
            value = (fontlist.WIDTH_CONDENSED + fontlist.WIDTH_NORMAL) / 2
        elif value == 'regular':
            comp = operator.gt
            value = (fontlist.WIDTH_CONDENSED + fontlist.WIDTH_NORMAL) / 2
        else:
            value = float(value)

        self.comp = comp
        self.value = value

    def match(self, font):
        return self.comp(font.width, self.value)


@add_matcher('--characters', '--chars', '-c',
             metavar=_('ABCXYZ'),
             help=_('Select fonts that contain the given characters.'))
class Characters(Matcher):

    slow = True

    def set_args(self, args):
        self.args = args

        self.match = get_character_matcher(self.arg, qt=self.args.qt)
        self.uses_extended = self.match.uses_extended


@add_matcher('--any-character', '--any-char',
             metavar=_('ABCXYZ'),
             help=_('Select fonts that contain the given characters.'))
class AnyCharacter(Matcher):

    slow = True

    def set_args(self, args):
        self.args = args

        self.match = get_character_matcher(self.arg, qt=self.args.qt,
                                                     contains_all=False)
        self.uses_extended = self.match.uses_extended


@filtering.set_cmdline_processor
def add_filter_matcher(cls, *options, **kwargs):

    antioptions = [opt.replace('--', '--no-', 1)
                   for opt in options if opt.startswith('--')]

    if cls.is_group:
        return

    if cls.is_switch:
        @add_matcher(*options, nargs=0, **kwargs)
        class FilterMatcher(Matcher):
            def __init__(self):
                self.match = cls(True).accept

        @add_matcher(*antioptions, nargs=0, **kwargs)
        class FilterMatcher(Matcher):
            def __init__(self):
                self.match = cls(False).accept
        return

    if cls.is_invertible:
        @add_matcher(*options, **kwargs)
        class FilterMatcher(Matcher):
            def __init__(self, arg):
                self.match = cls.fromstring(arg, True).accept

        @add_matcher(*antioptions, **kwargs)
        class FilterMatcher(Matcher):
            def __init__(self, arg):
                self.match = cls.fromstring(arg, False).accept
        return

    @add_matcher(*options, **kwargs)
    class FilterMatcher(Matcher):
        def __init__(self, arg):
            self.match = cls.fromstring(arg).accept




find_argparser.add_argument('--qt', const=True, default=AUTO,
                            action='store_const', dest='qt',
                            help=_('Use Qt (default is to guess)'))

find_argparser.add_argument('--no-qt', const=False, default=AUTO,
                            action='store_const', dest='qt',
                            help=_('Do not use Qt (default is to guess). '
                                   'This breaks universal character checks.'))

find_argparser.add_argument('--progress', const=True, default=AUTO,
                            action='store_const', dest='progress',
                            help=_('Use progress (default is to guess)'))

find_argparser.add_argument('--no-progress', const=False, default=AUTO,
                            action='store_const', dest='progress',
                            help=_('Do not use progress (default is to guess)'))

if fontlist.FontFinder.fcmatch_supported():
    find_argparser.add_argument('--fc-match', help='Use fc-match pattern')
    find_argparser.add_argument('--prune', action='store_true',
                                help=_('Prune fc-match matches'))
else:
    find_argparser.set_defaults(fc_match=None, prune=False)


find_argparser.add_argument('--no-localization', '-C', action='store_true',
                            help=_("Do not localize font strings"))

find_argparser.add_argument('--show-styles', '-y', action='store_true',
                            help=_("Display styles"))

find_argparser.add_argument('--show-paths', '-l', action='store_true',
                            help=_("Display files"))

find_argparser.add_argument('--format', metavar=_('TEMPLATE'),
                            help=_("Use the TEMPLATE as printing format"))

find_argparser.add_argument('--output', '-o', type=argparse.FileType('w'),
                            default=sys.stdout, metavar=_("FILE"),
                            help=_("Write fonts to FILE instead of "
                                   "standard output"))

find_argparser.add_argument('--expression', '--expr', '-e',
                            metavar=_('PRED'),
                            nargs='+',
                            help=_("Match fonts using an expression. "
                                   "The expression can contain all predicates "
                                   "options, without the leading dashes, as "
                                   "well as keywords 'or', 'and' and "
                                   "brackets for grouping."))

def find_fonts(*a, **kw):

    """Command line utility to find fonts."""

    args = find_argparser.parse_args(*a, **kw)

    # Get Qt early so that matchers can use it
    qt = args.qt

    if qt is AUTO:

        qt = False

        #if 'DISPLAY' in os.environ:
        #    try:
        #        from typeatlas.compat import QtGui, QtWidgets
        #    except ImportError:
        #        pass
        #    else:
        #        QtGui
        #        qt = True

    if qt:
        from typeatlas.compat import QtWidgets
        from typeatlas import qfontlist
        from typeatlas.uitools import QtExecutor
        app = QtWidgets.QApplication([])
        w = QtWidgets.QWidget()
        finder = qfontlist.QtFontFinder(executor=QtExecutor(parent=w))

    else:
        finder = fontlist.FontFinder()

    matcherkey = lambda matcher: matcher.disjunctive_group or ''
    matchers = sorted(get_matchers(args), key=matcherkey)

    progress = args.progress

    uses_extended = False

    for matcher in matchers:
        if matcher.uses_extended:
            uses_extended = True
        if matcher.slow:
            if progress is AUTO:
                progress = True

    if progress is AUTO:
        progress = uses_extended

    if not isatty(sys.stderr):
        progress = False

    print_format = FAMILY_PRINT_FORMAT

    show_styles = False
    if args.show_styles:
        show_styles = True
        print_format = STYLE_PRINT_FORMAT

    if args.show_paths:
        show_styles = True
        print_format = FILE_PRINT_FORMAT

    if args.format is not None:
        print_format = args.format.replace('\\n', '\n')

    def print_item(item):

        fields = {}
        for prop in fontlist.properties:
            name = prop.propname
            if prop.localized and not args.no_localization:
                value = item.translate(name, textlang())
            else:
                value = getattr(item, name)

            fields[name] = value
        print(print_format.format(**fields), file=args.output, end='')

    def match_item(item):
        # This gets read every time its accessed, unless we keep reference to
        # it.
        if uses_extended:
            extended = item.extended()
            extended

        for disjunctive_group, matcher_group in groupby(matchers, matcherkey):
            require = all if not disjunctive_group else any
            if not require(matcher.match(item) for matcher in matcher_group):
                return False
        return True

    if args.fc_match:
        fonts = finder.fcmatch(args.fc_match, many=True, all=not args.prune)
    else:
        fonts = finder.fonts()

    families = list(fontlist.get_families(fonts))
    def start_check():
        if progress:
            part_done = i / len(families)
            stars = int(part_done * 15)
            spaces  = int(15 - stars)
            sys.stderr.write('[' + '*' * stars + ' ' * spaces + ']: ')
            sys.stderr.write('%3.0f%%; ' % (part_done * 100, ))
            sys.stderr.write(_('%d out of %d families processed...')
                                    % (i, len(families)))
            sys.stderr.flush()

    def end_check():
        if progress:
            sys.stderr.write(tty_clear(sys.stderr))
            sys.stderr.flush()

    for i, family in enumerate(families):
        if not show_styles:
            start_check()
            is_match = any(match_item(style) for style in family.styles)
            end_check()

            if is_match:
                print_item(family)
        else:

            for style in family.styles:
                start_check()
                is_match = match_item(style)
                end_check()

                if is_match:
                    print_item(style)
