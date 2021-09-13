#!/usr/bin/env python<PYVERSION>
# -*- coding: utf-8; mode: python; -*-
<LICENSE_HEADER>
"""
Command line inputs
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from argcomplete import autocomplete

def _cli() -> ArgumentParser:
    """
    Parser for autodoc
    """
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    # python bash/zsh completion
    autocomplete(parser)
    return parser

def cli() -> dict:
    """
    Command line arguments
    """
    parser = _cli()
    return vars(parser.parse_args())
