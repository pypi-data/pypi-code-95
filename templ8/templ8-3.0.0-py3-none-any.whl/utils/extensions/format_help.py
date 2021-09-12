from argparse import ArgumentParser


def format_help(parser: ArgumentParser) -> None:
    help_action = parser._actions[0]  # pylint: disable = W0212

    if help_action.help is not None:
        help_action.help += "."
