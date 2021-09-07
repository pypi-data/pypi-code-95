import argparse
import sys

from racetrack_client import __version__
from racetrack_client.client.deploy import send_deploy_request
from racetrack_client.client.logs import show_logs
from racetrack_client.client_config.update import set_credentials, set_config_setting, set_config_url_alias
from racetrack_client.log.exception import log_exception
from racetrack_client.log.logs import configure_logs
from racetrack_client.manifest.validate import load_validated_manifest


def main():
    parser = argparse.ArgumentParser(description='CLI client tool for deploying workloads to Racetrack')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='enable verbose mode')
    subparsers = parser.add_subparsers()

    def _print_help(_: argparse.Namespace):
        parser.print_help(sys.stderr)

    parser.set_defaults(func=_print_help)

    # racetrack deploy
    parser_deploy = subparsers.add_parser(
        'deploy', help='Send request deploying a Fatman to the Racetrack cluster')
    parser_deploy.add_argument('workdir', default='.', nargs='?', help='directory with fatman.yaml manifest')
    parser_deploy.add_argument('racetrack_url', default='', nargs='?', help='URL to Racetrack server or alias name')
    parser_deploy.set_defaults(func=_deploy)

    # racetrack validate
    parser_validate = subparsers.add_parser('validate', help='Validate Fatman manifest file')
    parser_validate.add_argument('path', default='.', nargs='?',
                                 help='path to a Fatman manifest file or to a directory with it')
    parser_validate.set_defaults(func=_validate)

    # racetrack logs
    parser_logs = subparsers.add_parser('logs', help='Show logs from fatman output')
    parser_logs.add_argument('workdir', default='.', nargs='?', help='directory with fatman.yaml manifest')
    parser_logs.add_argument('racetrack_url', default='', nargs='?', help='URL to Racetrack server or alias name')
    parser_logs.add_argument('--tail', default=20, nargs='?', type=int, help='number of recent lines to show')
    parser_logs.set_defaults(func=_logs)

    # racetrack version
    parser_version = subparsers.add_parser('version', help='Show the version information')
    parser_version.set_defaults(func=_version)

    # racetrack config
    parser_config = subparsers.add_parser('config', help='Set local options for a Racetrack client')
    subparsers_config = parser_config.add_subparsers()

    # racetrack config racetrack_url
    parser_config_racetrack_url = subparsers_config.add_parser(
        'racetrack_url', help='Set default Racetrack URL address')
    parser_config_racetrack_url.add_argument('setting_value', help='setting value')
    parser_config_racetrack_url.set_defaults(func=_set_config_racetrack_url)

    # racetrack config credentials
    parser_config_credentials = subparsers_config.add_parser(
        'credentials', help='Manage credentials for git repository access')
    subparsers_config_credentials = parser_config_credentials.add_subparsers()

    # racetrack config credentials set
    parser_config_credentials_set = subparsers_config_credentials.add_parser(
        'set', help='Set credentials for reading git repository')
    parser_config_credentials_set.add_argument('repo_url', help='git remote URL')
    parser_config_credentials_set.add_argument('username', help='username for git authentication')
    parser_config_credentials_set.add_argument('token_password', help='password or token for git authentication')
    parser_config_credentials_set.set_defaults(func=_set_config_credentials)

    # racetrack config alias
    parser_config_alias = subparsers_config.add_parser('alias', help='Manage aliases for Racetrack server URLs')
    subparsers_config_alias = parser_config_alias.add_subparsers()

    # racetrack config alias set
    parser_config_alias_set = subparsers_config_alias.add_parser(
        'set', help='Set up an alias for Racetrack server URL')
    parser_config_alias_set.add_argument('alias', help='short name for an environment')
    parser_config_alias_set.add_argument('racetrack_url', help='Racetrack server URL address')
    parser_config_alias_set.set_defaults(func=_set_config_url_alias)

    args: argparse.Namespace = parser.parse_args()

    try:
        configure_logs(args.verbose)
        args.func(args)
    except Exception as e:
        log_exception(e)


def _deploy(args: argparse.Namespace):
    send_deploy_request(args.workdir, lifecycle_url=args.racetrack_url)


def _validate(args: argparse.Namespace):
    load_validated_manifest(args.path)


def _set_config_credentials(args: argparse.Namespace):
    set_credentials(args.repo_url, args.username, args.token_password)


def _set_config_racetrack_url(args: argparse.Namespace):
    set_config_setting('racetrack_url', args.setting_value)


def _set_config_url_alias(args: argparse.Namespace):
    set_config_url_alias(args.alias, args.racetrack_url)


def _logs(args: argparse.Namespace):
    show_logs(args.workdir, args.racetrack_url, args.tail)


def _version(_: argparse.Namespace):
    print(f'racetrack-client version {__version__}')
