
import os
import sys
import logging
import argparse

def main():
    from .__init__ import __version__
    from .file_handler import get_user_config_path

    description = "Stitch mosaics from Cockpit with (or without) ROIs."
    config_path, _ = get_user_config_path()
    if config_path is not None and config_path.exists():
        description += f" User config can be found at {config_path}."

    parser = argparse.ArgumentParser(prog="StitchM", description=description, add_help=False)
    stitch_group = parser.add_argument_group("Stitching arguments")
    stitch_group.add_argument(
        "-m", "--mosaic", metavar="PATH/TO/MOSAIC_FILE.TXT", dest="mosaic",
        type=str, default="", action='store',
        help="the mosaic to be stitched (.txt file)")
    stitch_group.add_argument(
        "-a", "--markers", metavar="PATH/TO/MARKER_FILE.TXT", dest="markers",
        type=str, default="", action='store',
        help="[OPTIONAL] the markers to be added as ROIs (.txt file)")
    stitch_group.add_argument(
        "-n", "--no-normalisation", dest="normalise",
        default=True, action='store_false',
        help="do not normalise images")

    setup_subparsers = parser.add_subparsers(title="Setup options", description="enter `StitchM setup -h` for details")
    setup_parser = setup_subparsers.add_parser(name="setup", add_help=False)
    setup_parser.add_argument(
        "-w", "--windows-shortcut", dest="windows_shortcut",
        action='store_true',
        help=(
            "creates a Windows shortcut on the user's desktop that accepts drag " +
            "and dropped files (one mosaic at a time, optionally including markers)"))
    setup_parser.add_argument(
        "-c", "--config", dest="config",
        action='store_true',
        help="creates a user specific config if called")
    
    setup_info_group = setup_parser.add_argument_group("Setup info")
    setup_info_group.add_argument('-h', '--help', action='help', help="show this help message and exit")

    package_group = parser.add_argument_group("Package info")
    package_group.add_argument('-v', '--version', action='version', version="%(prog)s {}".format(__version__))
    package_group.add_argument('-h', '--help', action='help', help="show this help message and exit")

    # if args has the attribute 'config', the setup subparser has been called and args.win will also exist
    if "setup" in sys.argv:
        from .log_handler import LogHandler
        with LogHandler("info", "info"):
            setup_args = parser.parse_args(namespace=setup_parser)
            if setup_args.windows_shortcut:
                from .file_handler import create_Windows_shortcut
                create_Windows_shortcut()
            if setup_args.config:
                from .file_handler import create_user_config
                create_user_config()
            if not setup_args.windows_shortcut and not setup_args.config:
                setup_parser.print_help()
        return

    args = parser.parse_args()
    # Empty strings are False
    if args.mosaic:
        from .file_handler import get_config
        from .log_handler import LogHandler
        from .run import main_run

        try:
            config, config_messages = get_config()
            with LogHandler(config=config, config_messages=config_messages):
                kwargs = vars(args)
                main_run(config, **kwargs)
        except Exception:
            logging.error('Error has occurred. Please see traceback for more info.', exc_info=True)
    else:
        parser.print_help()
