# Copyright (c) 2021, Thomas Aglassinger
# All rights reserved. Distributed under the BSD 3-Clause License.
import argparse
import glob
import logging
import sys

from . import __version__, log
from .sanitize import sanitize_file


def _parsed_args(args=None):
    parser = argparse.ArgumentParser(description="Sanitize PO files from gettext for version control")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "po_paths",
        metavar="PO-FILE",
        # NOTE: We should be able to use type=argparse.FileType("r") here.
        #  However, when passing multiple files this results in
        #  ResourceWarning: unclosed file <_io.TextIOWrapper...>.
        nargs="+",
        help='PO file(s) to sanitize; use glob patterns to process multiple files; use "**" for recursive scans',
    )
    return parser.parse_args(args)


def main_without_logging_setup(args=None) -> int:
    result = 0
    po_path = None
    sanitized_file_count = 0
    arguments = _parsed_args(args)
    try:
        for po_path_pattern in arguments.po_paths:
            for po_path in glob.iglob(po_path_pattern, recursive=True):
                sanitize_file(po_path)
                sanitized_file_count += 1
    except Exception as error:
        log.error('cannot sanitize "%s": %s', po_path, error)
        result = 1
    if result == 0:
        if sanitized_file_count >= 1:
            log.info("sanitized %d file(s)", sanitized_file_count)
        else:
            log.error("cannot find any PO-FILE matching the specified glob pattern(s)")
            result = 1
    return result


def main(args=None) -> int:
    logging.basicConfig(level=logging.INFO)
    return main_without_logging_setup(args)


if __name__ == "__main__":
    sys.exit(main())
