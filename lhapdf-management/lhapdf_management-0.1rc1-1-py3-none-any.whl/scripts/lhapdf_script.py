#!/usr/bin/env python3
"""
    Main LHAPDF management script
"""
import logging
import sys
from pathlib import Path
import argparse

from lhapdf_management.configuration import environment
from lhapdf_management import management

logger = logging.getLogger(__name__)


class ArgumentParser(argparse.ArgumentParser):
    """Overrides the error message for the argument parser to ensure the help is printed"""

    def error(self, message):
        self.print_help(sys.stderr)
        super().error(message)


class Runner:
    """Controls the running of the script
    It can be used programatically by using the flag ``interactive=True``
    """

    def __init__(self, interactive=False):
        # Accepted modes
        modes = [i for i in dir(self) if not i.startswith("_")]

        # Create aliases
        self.ls = self.list
        self.get = self.install
        self.upgrade = lambda *x: self.install(*(list(x) + ["--upgrade"]))

        self._interactive = interactive

        if interactive:
            # In interactive mode no global option is parsed
            # (if the environment needs to be changed it should be done manually)
            self._parser = ArgumentParser(add_help=False)
            return

        # Initiate the parsers
        main_parser = ArgumentParser(description=__doc__, add_help=False)

        main_parser.add_argument(
            "--pdfdir", type=Path, help="Local path where the PDF sets are located"
        )
        main_parser.add_argument(
            "--listdir", type=Path, help="Local path where the PDF index is located"
        )
        main_parser.add_argument(
            "--sources", type=str, nargs="+", default=[], help="Sources to look for remote data"
        )

        # First ask for the mode (and other global variables)
        self._parser = ArgumentParser(parents=[main_parser])
        main_parser.add_argument("mode", help=f"One of {modes}", type=str)

        main_args, remaining_args = main_parser.parse_known_args()

        if main_args.pdfdir:
            environment.datapath = main_args.pdfdir
        if main_args.listdir:
            environment.listdir = main_args.listdir
        for new_source in main_args.sources:
            environment.add_source(new_source)

        # Select mode (and add it to the program name which is useful for the error
        # and I hope it doesn't break anything in the way
        prog_mode = main_args.mode
        self._parser.prog += f" {prog_mode}"

        getattr(self, prog_mode)(*remaining_args)

    def list(self, *extra_args):
        """List available PDF sets, optionally filtered and/or categorised by status"""
        list_args = self._parser.add_argument_group("list arguments")
        list_args.add_argument("PATTERNS", nargs="*", help="Patterns to match PDF set against")
        list_args.add_argument("--installed", help="Show only installed sets", action="store_true")
        list_args.add_argument("--codes", help="Show ID codes", action="store_true")
        # TODO
        # --outdated: show which pdfs are outdated
        args = self._parser.parse_args(extra_args)

        if args.installed:
            index_db = management.get_installed_list()
        else:
            index_db = management.get_reference_list()

        if args.PATTERNS:
            # If any of the patterns matches a PDF, the PDF will be printed
            index_db = filter(lambda x: any(x.match(k) for k in args.PATTERNS), index_db)

        if self._interactive:
            return index_db

        for pdf in index_db:
            if args.codes:
                print(f"{pdf.id_code} {pdf.name}")
            else:
                print(pdf.name)

    def update(self, *extra_args):
        """Download and install a new PDF set index file"""
        _ = self._parser.parse_args(extra_args)
        return management.update_reference_file()

    def install(self, *extra_args):
        """Download and install new PDF set data files"""
        install_args = self._parser.add_argument_group("install arguments")
        install_args.add_argument("pdf_name", help="PDF to download")
        install_args.add_argument(
            "--upgrade",
            help="Download and install a newer replacement if available",
            action="store_true",
        )
        install_args.add_argument("--keep", help="Keep the downloaded tarball", action="store_true")
        args = self._parser.parse_args(extra_args)
        return management.install_pdf(args.pdf_name, upgrade=args.upgrade, keep=args.keep)


def main():
    Runner()


if __name__ == "__main__":
    main()
