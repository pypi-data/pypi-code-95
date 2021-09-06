# -*- coding: utf-8 -*-
"""
    binalyzer.cli
    ~~~~~~~~~~~~~

    This module implements the entry point used by the command line interface.

    :copyright: 2020 Denis Vasilík
    :license: MIT, see LICENSE for details.
"""
import sys

from binalyzer_cli.cli import BinalyzerGroup


cli = BinalyzerGroup()
cli.name = "binalyzer"


def main():
    cli.main(args=sys.argv[1:])


if __name__ == "__main__":
    main()
