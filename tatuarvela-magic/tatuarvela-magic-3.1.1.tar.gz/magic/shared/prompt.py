import sys

from magic.shared.display import Color, clear_last_line, in_color
from magic.shared.validation import is_yes_or_no


def prompt(
    message,
    color=Color.WHITE,
    validate=None,
    default=None,
    required=False,
):
    print(in_color(message, color))

    return __prompt_input(validate, default, required)


def multiline_prompt(
    message, color=Color.WHITE, validate=None, default=None, required=False
):
    print(in_color(message, color))

    lines = []
    while True:
        line = __prompt_input(validate, default)
        if line:
            lines.append(line)
        elif not required or len(lines) > 0:
            clear_last_line()
            break
    return lines


def yes_or_no_prompt(message, color=Color.WHITE, default=None, required=False):
    print(in_color(message, color))

    return __yes_or_no(__prompt_input(is_yes_or_no, default, required))


def __yes_or_no(value):
    if value in ("y", "yes"):
        return True
    return False


def __prompt_input(validate=None, default=None, required=False):
    input_message = "> "

    response = None
    while response is None:
        try:
            response = input(in_color(input_message, Color.CYAN))
        except KeyboardInterrupt:
            sys.exit()

        if default is not None:
            if response == "":
                clear_last_line()
                print(in_color(f"{input_message}{default}", Color.CYAN))
                response = default

        if required and response == "":
            response = None
            clear_last_line()

        if validate is not None:
            if validate(response) is False:
                response = None
                clear_last_line()

    return response
