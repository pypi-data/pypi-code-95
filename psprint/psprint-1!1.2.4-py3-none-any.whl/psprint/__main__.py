#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020, 2021 Pradyumna Paranjape
# This file is part of psprint.
#
# psprint is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# psprint is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with psprint.  If not, see <https://www.gnu.org/licenses/>.
#
'''
module call
'''

from . import DEFAULT_PRINT, init_print

# Pass custom configuration here
CUSTOM_PRINT = init_print(custom=None)

# Some recipes are pre-initiated in psprint.__init__.py:
# psprint.DEFAULT_PRINT is initiated similarly as above
# psprint.print is psprint.DEFAULT_PRINT's psprint function
assert CUSTOM_PRINT == DEFAULT_PRINT

# Modify FLAGS
CUSTOM_PRINT.switches['short'] = False
CUSTOM_PRINT.switches['pad'] = True
# Standard flags should be specified in config file

# Add an InfoMark (style) 'in the script'
CUSTOM_PRINT.edit_style(pref='DOCS',
                        mark='docs',
                        pref_gloss='bright',
                        text_color='light blue')
# Multiple InfoMarks should be supplied through config file

# overload __builtin__.print to psprint.print
print = CUSTOM_PRINT.psprint
# If no customizations are intended, simply import psprint.print


def main():
    """
    main function call
    """
    # An iterable object
    edit_style_instructions = {
        'config': 'Pass custom config to psprint.init_print',
        'script': 'Edit psprint.DEFAULT_PRINT instance'
    }

    # Without any arguments, __builtin__.print() is called
    print()
    # Notice that blank lines don't have padding spaces

    # ``mark`` applies indicator styles
    print('usage:', mark='err')

    # Default mark is 'cont' i.e. no ``pref``, only padding
    print('Use me as an imported module')

    # Marks may be supplied as str, int or InfoMark objects
    print('Read usage instructions:', mark=1)

    # Using 'Non-shipped' mark, created on line 40
    print('https://pradyparanjpe.gitlab.io/psprint/usage.html', mark='docs')

    # 'shipped' marks are
    # 0: 'cont', 1: 'info', 2: 'act', 3: 'list', 4: 'warn', 5: 'err', 6: 'bug'
    print('from psprint import print', mark='act')
    print('from psprint import psfmt', mark='act')
    print('To edit styles, you may implement (any):', mark='info')

    # Iterable objects are resolved if instructed
    # Text may be indented (indentation level = 2 * <spaces>)
    print(edit_style_instructions, mark='act', indent=1, iterate=True)

    # __builtin__.print's kwargs are sincerely conveyed
    print('Capabilities are illustrated in',
          '``this``',
          'very file',
          mark='info',
          indent=2,
          sep=' ',
          end='\n')

    # ``pref`` and ``text`` style may be customized `on-the-fly`
    print(__file__, mark='docs', pref='FILE')

    # mark='bug' is a useful search query to sanitize debug code
    print('Bye', mark='bug')
    # print('User may ignore all lines marked with [DEBUG]', mark='bug')

    print()


if __name__ in ('__main__', 'psprint.__main__'):
    main()
