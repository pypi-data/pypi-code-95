# -*- coding: utf-8 -*-
#
#    TypeAtlas CLI Charset Functions
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

import sys
import argparse
import unicodedata

from typeatlas.langutil import _, N_, textlang, LanguageDatabase
from typeatlas.charinfo import CharacterDatabase, all_character_codes
from typeatlas.charsets import get_encoding


def get_encoding_failing(name, *args, **kwargs):
    result = get_encoding(name, *args, **kwargs)
    if result is None:
        raise KeyError(name)
    return result


charset_argparser = argparse.ArgumentParser(_('TypeAtlas character map'))

charset_argparser.add_argument(
        '--script', '-s',
        help=_('Display the given script'))

charset_argparser.add_argument(
        '--charset', '-C', type=get_encoding_failing,
        help=_('Display the given character set'))

charset_argparser.add_argument(
        '--block', '-B',
        help='Unicode block')

charset_argparser.add_argument(
        'needle', nargs='*',
        help=_('Search for characters related to a word'))


def charwidth(char):
    """Return the width of the character."""
    if unicodedata.east_asian_width(char) in 'WF':
        return 2
    category = unicodedata.category(char)
    if category == 'Cc':
        return -1
    if char in '\x00\u034F\u200B\u200F\u2028\u2029\u202A\u202E\u2060\u2063':
        return 0
    if unicodedata.combining(char):
        return 0
    return 1


class CharPrinter(object):

    def __init__(self, output=sys.stdout):
        self.output = output
        self._chardb = None
        self._langdb = None

    @property
    def langdb(self):
        if self._langdb is None:
            self._langdb = LanguageDatabase.get_instance(populated=True)
        return self._langdb

    @property
    def chardb(self):
        if self._chardb is None:
            self._chardb = CharacterDatabase.get_instance(populated=True)
        return self._chardb

    def print_table_header(self):
        print('%12s' % ('', ), end='', file=self.output)

        for i in range(0, 0xf + 1):
            print('  %1X' % (i, ), end='', file=self.output)

        print(file=self.output)

    def print_table(self, characters):

        row = -float('inf')

        for i, char in characters:
            if not (row <= i <= row + 0xf):
                newrow = i & ~0xf

                if abs(row - newrow) > 0x10:
                    if row > -float('inf'):
                        print(file=self.output)
                        print(file=self.output)
                    self.print_table_header()
                else:
                    print(file=self.output)

                row = newrow

                print('%11X_' % (row >> 4, ), end='', file=self.output)

                for j in range(row, i):
                    print(' %*s' % (2, ''), end='', file=self.output)

            #info = self.chardb.get(ord(char))
            #if info.display:
            #    char = chr(info.display)

            width = charwidth(char)
            if unicodedata.category(char) == 'Cc':
                print(' %*s' % (2, ''), end='', file=self.output)
            elif unicodedata.combining(char):
                print(' %1s%s' % ('', 'o' + char), end='', file=self.output)
            else:
                print(' %*s%s' % (2 - width, '', char), end='',
                      file=self.output)

        print(file=self.output)

    def print_character(self, code, char):
        if self.chardb is None:
            self.chardb = CharacterDatabase.getinstance(populated=True)

        info = self.chardb.get(ord(char), autofill=True)
        script = self.chardb.find_script_name(self.langdb, ord(char))
        plane = self.chardb.get_plane(ord(char))

        print ("%15s: %X" % (_("Hex code"), code), file=self.output)
        print ("%15s: %s" % (_("Character"), char), file=self.output)
        print ("%15s: %s" % (_("Category"), info.category_name(translate=_)),
            file=self.output)
        print ("%15s: %s" % (_("Block"), info.block.name), file=self.output)
        print ("%15s: %s" % (_("Script"), script), file=self.output)
        print ("%15s: %d - %s" % (_("Plane"), plane.number,
                                  _(plane.description)),
               file=self.output)

        for alias in info.aliases:
            print('= ' + alias, file=self.output)
        for alias in info.formalaliases:
            print(info.formal_alias + ' ' + alias, file=self.output)
        for variation in info.variations:
            print ("%15s: %s" % (_("Variation"), variation), file=self.output)

    def select_characters(self, args):
        codes = {}
        selectors = []

        if args.script:
            script = self.chardb.get_alias_value('sc', args.script)
            selectors.append(lambda c: self.chardb.find_script(c) == script)
        if args.block:
            block = args.block
            selectors.append(lambda c: self.chardb.get(c).block == block)

        if not selectors and not args.charset:
            return ((c, chr(c)) for c in range(128))

        elif args.charset is not None:
            charset = args.charset.complete()
            characters = map(ord, charset.characters)
        else:
            charset = None
            characters = all_character_codes()

        for selector in selectors:
            characters = filter(selector, characters)

        if charset is not None:
            return sorted((charset.get_integer(c), chr(c)) for c in characters)

        return sorted((c, chr(c)) for c in characters)


def display_characters(*a, **kw):

    """Command line utility to display character maps."""

    args = charset_argparser.parse_args(*a, **kw)
    printer = CharPrinter()
    characters = printer.select_characters(args)

    printer.print_table(printer.select_characters(args))


if __name__ == '__main__':
    display_characters()
