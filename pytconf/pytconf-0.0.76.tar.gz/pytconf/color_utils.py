from termcolor import colored, cprint


def print_highlight(text):
    cprint(text=text, color="white", attrs=["bold"])


def print_warn(text):
    cprint(text=text, color="red", attrs=["bold"])


def print_error(text):
    cprint(text=text, color="red", attrs=["bold"])


def print_title(text):
    cprint(text=text, color="green", attrs=[])


def color_hi(text):
    return colored(text=text, color="white", attrs=["bold"])


def color_warn(text):
    return colored(text=text, color="red", attrs=["bold"])


def color_ok(text):
    return colored(text=text, color="green", attrs=["bold"])
