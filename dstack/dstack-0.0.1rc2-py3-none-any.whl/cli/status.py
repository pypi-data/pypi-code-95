import sys
from argparse import Namespace

from dstack.cli.common import print_runs_and_jobs
from dstack.config import get_config, ConfigurationError


def status_func(args: Namespace):
    try:
        dstack_config = get_config()
        # TODO: Support non-default profiles
        profile = dstack_config.get_profile("default")
        print_runs_and_jobs(profile, args)
    except ConfigurationError:
        sys.exit(f"Call 'dstack login' or 'dstack register' first")


def register_parsers(main_subparsers):
    parser = main_subparsers.add_parser("status", help="List runs and jobs")

    parser.add_argument('run_name', metavar='RUN', type=str, nargs='?')
    parser.add_argument("-n", "--last", help="Include n last submitted runs (of any status)", dest="n", type=int,
                        nargs="?")
    parser.add_argument("--no-jobs", help="Don't include jobs", dest="no_jobs", action="store_true")

    parser.set_defaults(func=status_func)
