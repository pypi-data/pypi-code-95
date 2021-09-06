from argparse import Namespace

import requests

from dstack.cli import get_or_ask, confirm
from dstack.config import get_config, API_SERVER, _get_config_path, from_yaml_file, Profile


def login_func(args: Namespace):
    dstack_config = from_yaml_file(_get_config_path(None))
    # TODO: Support non-default profiles
    profile = dstack_config.get_profile("default")
    if profile is None:
        profile = Profile("default", None, args.server, not args.no_verify)

    if args.server is not None:
        profile.server = args.server
    profile.verify = not args.no_verify

    user = valid_user_name(args)
    password = valid_password(args)

    login_params = {
        "user": user,
        "password": password
    }
    headers = {
        "Content-Type": f"application/json; charset=utf-8"
    }
    login_response = requests.request(method="GET", url=f"{profile.server}/users/login", params=login_params,
                                      headers=headers,
                                      verify=profile.verify)
    if login_response.status_code == 200:
        token = login_response.json()["token"]
        if args.force or (token != profile.token and confirm(
                f"Do you want to replace the token for the profile 'default'")):
            # f"Do you want to replace the token for the profile '{args.profile}'")):
            profile.token = token

            dstack_config.add_or_replace_profile(profile)
            dstack_config.save()
            print("Login succeeded")
    else:
        response_json = login_response.json()
        if response_json.get("message") is not None:
            print(response_json["message"])
        else:
            login_response.raise_for_status()


def valid_password(args):
    return get_or_ask(args, None, "password", "Password: ", secure=True)


def valid_email(args):
    return get_or_ask(args, None, "email", "Email address: ", secure=False)


def valid_user_name(args):
    return get_or_ask(args, None, "user", "User name: ", secure=False)


# TODO: Add --reset argument
def register_parsers(main_subparsers):
    parser = main_subparsers.add_parser("login", help="Log in")

    parser.add_argument("-u", "--user", help="Set a user name", type=str, nargs="?")
    parser.add_argument("-p", "--password", help="Set a user email", type=str, nargs="?")

    parser.add_argument("--server", help="Set a server endpoint", type=str, nargs="?",
                        default=API_SERVER, const=API_SERVER)
    parser.add_argument("--no-verify", help="Do not verify SSL certificates", dest="no_verify", action="store_true")
    parser.add_argument("--force", help="Don't ask for confirmation", action="store_true")

    parser.set_defaults(func=login_func)
