#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-
# Copyright © 2020-2021 Pradyumna Paranjape
#
# This file is part of pspvis.
#
# pspvis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pspvis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pspvis. If not, see <https://www.gnu.org/licenses/>.
#
"""
Command-line Callable
"""

from pspvis import __version__
from pspvis.front_ui import TkUI
from pspvis.command_line import cli


def main():
    cli_args = cli()
    if cli_args['version']:
        print(__version__)
        return
    sheet = cli_args.get('sheet')
    TkUI(sheet=sheet).mainloop()


if __name__ == '__main__':
    main()
