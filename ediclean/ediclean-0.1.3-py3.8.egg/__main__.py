import argparse
import os
import sys
import logging
import ediclean
import ediclean.paxlst as paxlst


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        logging.error ("Directory does not exist: " + path)

def main() -> None:
    parser = argparse.ArgumentParser(
        prog='ediclean',
        description="Strip non-standard text blocks from UN/EDIFACT messages."
    )
    parser.add_argument('filename',
                        nargs='?',
                        help="File containing UN/EDIFACT PAXLST message")
    
    parser.add_argument('-s','--source_dir', type=dir_path)
    parser.add_argument('-t','--target_dir', type=dir_path)
    parser.add_argument('--version',
                    action="store_true",
                    help=argparse.SUPPRESS)

    try:
        args = parser.parse_args()
        if args.version:
            print("ediclean", ediclean.__version__)
        elif args.source_dir and not args.target_dir:
            print("Target directory missing")
        elif not args.source_dir and args.target_dir:
            print("Source directory missing")
        elif args.source_dir and args.target_dir:
            paxlst.cleandir(args.source_dir, args.target_dir, "")        
        elif not args.filename:
            parser.print_usage()
        elif args.filename:
            print(paxlst.cleanfile(args.filename))
        else:
            pass

    except SystemExit as err:
        if err.code == 2: parser.print_help()


if __name__ == '__main__':
    main()
