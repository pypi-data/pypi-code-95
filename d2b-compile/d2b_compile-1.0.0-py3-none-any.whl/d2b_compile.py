import argparse
from pathlib import Path

import compile_dcm2bids_config
from d2b.hookspecs import hookimpl


__version__ = "1.0.0"


@hookimpl
def register_commands(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("compile")
    parser.add_argument(
        "in_file",
        nargs="+",
        type=Path,
        help="The JSON config files to combine",
    )
    parser.add_argument(
        "-o",
        "--out-file",
        type=argparse.FileType("w", encoding="utf8"),
        default="-",
        help="The file to write the combined config file to. If not "
        "specified outputs are written to stdout.",
    )
    parser.set_defaults(handler=compile_dcm2bids_config._handler)
