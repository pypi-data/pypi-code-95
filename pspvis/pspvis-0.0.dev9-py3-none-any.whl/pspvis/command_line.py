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
Command line inputs
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path

from argcomplete import autocomplete


def _cli() -> ArgumentParser:
    """
    Parser for autodoc
    """
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('--version',
                        action='store_true',
                        help='display currently installed version and exit',
                        default=None)

    parser.add_argument('sheet',
                        type=Path,
                        nargs='?',
                        help='csv values file',
                        default=None)
    # python bash/zsh completion
    autocomplete(parser)
    return parser


def cli() -> dict:
    """
    Command line arguments
    """
    parser = _cli()
    return vars(parser.parse_args())
