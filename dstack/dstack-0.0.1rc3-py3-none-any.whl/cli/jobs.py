import os
import sys
from argparse import Namespace

from git import InvalidGitRepositoryError

from dstack.cli.common import print_jobs
from dstack.config import get_config, ConfigurationError


def jobs_func(args: Namespace):
    try:
        dstack_config = get_config()
        # TODO: Support non-default profiles
        profile = dstack_config.get_profile("default")
        print_jobs(args.run_name, profile)
    except InvalidGitRepositoryError:
        sys.exit(f"{os.getcwd()} is not a Git repo")
    except ConfigurationError:
        sys.exit(f"Call 'dstack login' or 'dstack register' first")


def register_parsers(main_subparsers):
    parser = main_subparsers.add_parser("jobs", help="List jobs")

    parser.add_argument('run_name', metavar='RUN', type=str, nargs='?')

    parser.set_defaults(func=jobs_func)
