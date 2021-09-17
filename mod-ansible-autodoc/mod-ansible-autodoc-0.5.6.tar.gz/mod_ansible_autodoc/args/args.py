import argparse
from typing import Dict
from mod_ansible_autodoc import name, __version__

ARG_NAMES = [
    "todo-title",
    "actions-title",
    "tags-title",
    "variables-title",
    "todo-description",
    "actions-description",
    "tags-description",
    "variables-description",
    "variable-title-prefix",
    "variable-title-postfix",
    "variable-example-comment-prefix",
    "version"
]

ARGS = [
    {"arg_name": ARG_NAMES[0], "arg_help": "todo markdown file title"},
    {"arg_name": ARG_NAMES[1], "arg_help": "actions markdown file title"},
    {"arg_name": ARG_NAMES[2], "arg_help": "tags markdown file title"},
    {"arg_name": ARG_NAMES[3], "arg_help": "variables md file title"},
    {"arg_name": ARG_NAMES[4], "arg_help": "todo markdown file description"},
    {"arg_name": ARG_NAMES[5], "arg_help": "actions markdown file description"},
    {"arg_name": ARG_NAMES[6], "arg_help": "tags markdown file description"},
    {"arg_name": ARG_NAMES[7], "arg_help": "variables md file description"},
    {"arg_name": ARG_NAMES[8], "arg_help": "variables section title prefix"},
    {"arg_name": ARG_NAMES[9], "arg_help": "variables section title postfix"},
    {"arg_name": ARG_NAMES[10], "arg_help": "variables example comment prefix"},
    {"arg_name": ARG_NAMES[11], "arg_help": "version of the package"},
]


def get_user_arguments() -> Dict[str, str]:
    """
    Configures argument parser, then gets the ones entered by the user

    Returns:
        Dict[str, str]: user arguments ({ name: value, ... })
    """
    parser = configure_parser()
    user_args = read_parser_args(parser)
    return user_args


def configure_parser() -> argparse.ArgumentParser:
    """
    Instantiates the argument parser instance and adds the accepted arguments

    Returns:
        argparse.ArgumentParser: parser
    """
    parser = argparse.ArgumentParser()
    for arg in ARGS:
        if arg.get("arg_name", None) == "version":
            parser.add_argument(
                "-v",
                f"--{arg.get('arg_name')}",
                action="version",
                version=f"{name} {__version__}",
                help=arg.get('arg_help')
            )
            continue

        parser.add_argument(
            f"--{arg.get('arg_name')}",
            help=arg.get('arg_help')
        )
    return parser


def read_parser_args(parser) -> Dict[str, str]:
    """
    Reads arguments entered by the user

    Args:
        parser (argparse.ArgumentParser): parser

    Returns:
        Dict[str, str]: user arguments ({ name: value, ... })
    """
    args = parser.parse_args()
    user_args = {}

    for arg in ARGS:
        # python's argparse changes dashes (-) to underscores (_) internally
        arg_name = arg.get("arg_name")
        formatted_arg_name = arg_name.replace("-", "_")

        # Get parsed argument
        parsed_arg_val = getattr(args, formatted_arg_name, None)
        if parsed_arg_val:
            user_args[arg_name] = parsed_arg_val

    # If --version is in arguments, make sure it's the only one
    if "version" in user_args.keys() and len(user_args) > 1:
        raise argparse.ArgumentError("Invalid option: \"version\"")

    return user_args
