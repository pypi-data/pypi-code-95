import json
from argparse import Namespace

import requests

from dstack.cli import get_or_ask, confirm
from dstack.config import get_config, API_SERVER, Profile, from_yaml_file, _get_config_path


def register_func(args: Namespace):
    dstack_config = from_yaml_file(_get_config_path(None))
    # TODO: Support non-default profiles
    profile = dstack_config.get_profile("default")
    if profile is None:
        profile = Profile("default", None, args.server, not args.no_verify)

    if args.server is not None:
        profile.server = args.server
    profile.verify = not args.no_verify

    user = valid_user_name(args)
    email = valid_email(args)
    password = valid_password(args)

    register_data = {
        "name": user,
        "email": email,
        "password": password
    }
    register_data_bytes = json.dumps(register_data).encode("utf-8")
    headers = {
        "Content-Type": f"application/json; charset=utf-8"
    }
    register_response = requests.request(method="POST", url=f"{profile.server}/users/register",
                                         data=register_data_bytes,
                                         headers=headers, verify=profile.verify)
    if register_response.status_code == 200:
        print("We've sent you an email with a verification code. Copy the code from the email and paste it here.")
        verification_code = input("Verification code: ")
        verify_params = {
            "user": user,
            "code": verification_code
        }
        verify_response = requests.request(method="GET", url=f"{profile.server}/users/verify", params=verify_params,
                                           headers=headers,
                                           verify=profile.verify)
        verify_response.raise_for_status()
        if verify_response.status_code == 200:
            token = verify_response.json()["token"]
            if args.force or (token != profile.token and confirm(
                    f"Do you want to replace the token for the profile 'default'")):
                # f"Do you want to replace the token for the profile '{args.profile}'")):
                profile.token = token

                dstack_config.add_or_replace_profile(profile)
                dstack_config.save()
                print("Registration succeeded")
    else:
        if register_response.status_code == 400:
            print(register_response.json()["message"])


def valid_password(args):
    return get_or_ask(args, None, "password", "Password: ", secure=True)


def valid_email(args):
    return get_or_ask(args, None, "email", "Email address: ", secure=False)


def valid_user_name(args):
    return get_or_ask(args, None, "user", "User name: ", secure=False)


def register_parsers(main_subparsers):
    parser = main_subparsers.add_parser("register", help="Register a user")

    parser.add_argument("-u", "--user",
                        help="Set a user name (only latin characters, digits, and underscores)",
                        type=str, nargs="?")
    parser.add_argument("-e", "--email", help="Set a user email", type=str, nargs="?")
    parser.add_argument("-p", "--password", help="Set a password", type=str, nargs="?")

    parser.add_argument("--server", help="Set a server endpoint", type=str, nargs="?",
                        default=API_SERVER, const=API_SERVER)
    parser.add_argument("--no-verify", help="Do not verify SSL certificates", dest="no_verify", action="store_true")
    parser.add_argument("--force", help="Don't ask for confirmation", action="store_true")

    parser.set_defaults(func=register_func)
