"""This file is executed when running the module directly."""

import os
import sys

from quickhtml import convert, convert_file

ARGS = sys.argv[1:]
MESSAGES = {
    "NO_ARGUMENT": "No file or string was provided. Use \"python -m quickhtml -h\" or \"python -m quickhtml --help\" to print a help message.",
    "HELP": "To convert Markdown into HTML, use \"python -m quickhtml [args]\", where [args] is a list of arguments, and each argument is either a file or a string.\nE.g.: \"python -m quickhtml FILE.md \"# This is a level 1 heading\" FILE_2.md\".\nTo export results to a file, use \"python -m quickhtml [args] > [out_file]\".\nTo see this message, run \"python -m quickhtml -h\" or \"python -m quickhtml --help\".",
}


def main():
    """Convert Markdown into HTML and print it to the terminal."""
    if not ARGS or all(arg.strip() == "" for arg in ARGS):
        print(MESSAGES["NO_ARGUMENT"])
    elif len(ARGS) == 1 and ARGS[0] in ("--help", "-h"):
        print(MESSAGES["HELP"])
    else:
        for arg in ARGS:
            print(convert_file(arg) if os.path.isfile(arg) else convert(arg))


if __name__ == "__main__":
    main()
