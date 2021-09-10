import argparse
import os
import sys
import ediclean
import ediclean.paxlst as paxlst


def main() -> None:
    parser = argparse.ArgumentParser(prog='ediclean', description="Clean UN/EDIFACT PAXLST files from unsupported characters.")
    parser.add_argument('filename', nargs='?', help="File containing UN/EDIFACT PAXLST message")
    parser.add_argument('--version', action="store_true", help=argparse.SUPPRESS)

    try:
        args = parser.parse_args()
        if args.version:
            print("ediclean", ediclean.__version__)
        elif not args.filename:
            parser.print_usage()
        elif args.filename:
            print (paxlst.cleanfile(args.filename))
        else:
            pass

    except SystemExit as err: 
        if err.code == 2: parser.print_help()


if __name__ == '__main__':
    main()
