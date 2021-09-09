# coding: utf-8

#
# Debian repo Contents files
#
# CLI bindings
#
###
# Copyright (c) 2010-2021  Stuart Prescott
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
###

""" Command line interface to pydebcontents """

import argparse
from pathlib import Path

from typing import Any, List, Optional, Union

from . import __version__
from . import contents_file


class Cli:
    """ Run a specified command sending output to stdout """

    def __init__(
        self,
        base: Union[str, Path],
        options: Any = None,
    ) -> None:
        self.base = base
        self.options = options

    @classmethod
    def main(cls, argv: Optional[List[str]] = None) -> bool:
        args = cls.parse_args(argv)

        runner = cls(base=args.base, options=args)

        success = args.func(runner, args)
        return not success

    def search(
        self,
        pattern: str,
        mode: str,
        release: str,
        arch: str,
        components: List[str],
        maxhits: int,
    ) -> bool:
        if not components:
            components = ["main", "contrib", "non-free"]
        archs = [arch, "all"]
        contents = contents_file.contents_file(
            self.base, release, archs, components, maxhits
        )

        regexp = contents_file.pattern2re(pattern, mode)

        print(regexp)
        packages = contents.search(regexp)
        packages.separator = "\n"
        print(str(packages))
        return len(packages) > 0

    @staticmethod
    def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
        description = """\
%(prog)s implements something akin to apt-file using Python modules."""

        parser = argparse.ArgumentParser(description=description, epilog="")

        # create sub commands for each import action to be performed
        commands = parser.add_subparsers(dest="command", required=True)

        default_release_parser = argparse.ArgumentParser(add_help=False)
        default_release_parser.add_argument(
            "--release",
            action="store",
            default="sid",
            metavar="RELEASE",
            help="release to search (default: sid)",
        )

        default_arch_parser = argparse.ArgumentParser(add_help=False)
        default_arch_parser.add_argument(
            "--arch",
            "--architecture",
            action="store",
            default="amd64",
            metavar="ARCH",
            help="architecture to search (default: amd64)",
        )

        default_component_parser = argparse.ArgumentParser(add_help=False)
        default_component_parser.add_argument(
            "--component",
            action="append",
            metavar="COMP",
            dest="components",
            help="archive components to search (default: all of them)",
        )

        # subcommands

        ### "search"
        subparser = commands.add_parser(
            "search",
            parents=[
                default_release_parser,
                default_arch_parser,
                default_component_parser,
            ],
            help="search for which packages contain a file.",
        )
        subparser.add_argument(
            "pattern",
            action="store",
            metavar="PATTERN",
            help="glob, regular expression or fixed string",
        )
        subparser.add_argument(
            "--mode",
            action="store",
            help="match mode for pattern",
            default="glob",
            choices=["glob", "regex", "fixed"],
        )
        subparser.add_argument(
            "--max",
            action="store",
            help="maximum number of packages to return",
            default=None,
            type=int,
        )
        subparser.set_defaults(
            func=lambda r, a: r.search(
                a.pattern, a.mode, a.release, a.arch, a.components, a.max
            )
        )

        ## General options
        parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s " + str(__version__),
            help="print version string and exit",
        )

        parser.add_argument(
            "--base",
            action="store",
            required=True,
            help="set the local path to the Debian mirror",
        )

        args = parser.parse_args(argv)

        return args


main = Cli.main
