#!/usr/bin/env python3
#
# cytr: stateless password manager and generator
#

import argparse
import base64
import hashlib
import time
from getpass import getpass

try:
    from cytr import __version__
except ImportError:
    __version__ = "1.4"


short_pass_length = 15
b64_altchars = b"42"
b85_altchar_33 = "["
b85_altchar_36 = "]"
b85_altchar_96 = "."


def hash_data(data: str):
    data_sha_64 = hashlib.sha256(data.encode()).hexdigest()

    # shorten the data hash to 32 chars string
    data_sha_32 = "".join(list(data_sha_64[i] for i in range(0, 64, 2)))

    return data_sha_32


def base85_encode(data_hash: str):
    password = base64.b85encode(data_hash.encode()).decode()

    password = password.replace("!", b85_altchar_33)
    password = password.replace("$", b85_altchar_36)
    password = password.replace("`", b85_altchar_96)

    return password


def generate_password(
    domain: str,
    username: str,
    master_password: str,
    domain_counter: int = 1,
):
    str_domain_counter = "" if domain_counter <= 1 else str(domain_counter)
    data = username + domain.lower() + str_domain_counter + master_password

    data_hash = hash_data(data)

    return base85_encode(data_hash)


def convert_short_simple(password: str, length: int = short_pass_length):
    """Encode the password to a shorter and simpler version."""
    simple_password = base64.b64encode(
        password.encode(), altchars=b64_altchars
    ).decode()
    return simple_password[:length]


def main():
    parser = argparse.ArgumentParser(
        prog="cytr",
        usage="cytr [domain] [username] [master_password] [options]",
        description="%(prog)s stateless password manager/generator.",
    )
    parser.add_argument("--version", action="store_true")
    parser.add_argument(
        "domain",
        help="Domain name/IP/service.",
        type=str,
        nargs="?",
    )
    parser.add_argument(
        "username",
        help="Username/Email/ID.",
        type=str,
        nargs="?",
    )
    parser.add_argument(
        "master_password",
        help="Master password used during the password generation.",
        type=str,
        nargs="?",
    )
    parser.add_argument(
        "-c",
        "--domain-counter",
        help="An integer representing the number of times you changed your "
        "password, increment to change password.",
        action="store",
        type=int,
        nargs="?",
        default=1,
    )
    parser.add_argument(
        "-s",
        "--short-simple",
        help="Short and simple password, generate a 15 char password variant "
        "instead of the 40 default, and without special characters.",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output the password, by default the password is added to the "
        "clipboard.",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--timer",
        help="Time before flushing the clipboard, default=20 (s), use 0 to "
        "disable the timer.",
        action="store",
        type=int,
        nargs="?",
        default=20,
    )

    return dispatch(parser)


def dispatch(parser):
    args = parser.parse_args()

    if args.version:
        print("cypred version {}".format(__version__))
        return 0

    domain = args.domain
    if domain is None:
        try:
            domain = str(input("domain: "))
        except KeyboardInterrupt:
            return 1

    username = args.username
    if username is None:
        try:
            username = str(input("username: "))
        except KeyboardInterrupt:
            return 1

    master_password = args.master_password
    if master_password is None:
        try:
            master_password = getpass("master password: ")
        except KeyboardInterrupt:
            return 1

    password = generate_password(
        domain=domain,
        username=username,
        master_password=master_password,
        domain_counter=args.domain_counter,
    )

    if args.short_simple:
        password = convert_short_simple(password)

    if args.output:
        print(password)
        return 0

    try:
        import pyperclip
    except ImportError:
        print("`pyperclip` is needed.\nYou can also use the `-o` flag.")
        return 1

    pyperclip.copy(password)
    timer = args.timer
    if timer and timer > 0:
        print("Password copied to the clipboard for {}s.".format(timer))
        try:
            time.sleep(timer)
        except KeyboardInterrupt:
            pass
        pyperclip.copy("")  # remove the content of the clipboard
    else:
        print("Password copied to the clipboard.")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
