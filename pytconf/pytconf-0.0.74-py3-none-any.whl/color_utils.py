from colored import stylize, fg, attr


def print_highlight(text):
    print(stylize(text, fg("white") + attr("bold")))


def print_warn(text):
    print(stylize(text, fg("red") + attr("bold")))


def print_error(text):
    print(stylize(text, fg("red") + attr("bold")))


def print_title(text):
    print(stylize(text, fg("green")))


def color_hi(text):
    return stylize(text, fg("white") + attr("bold"))


def color_warn(text):
    return stylize(text, fg("red") + attr("bold"))


def color_ok(text):
    return stylize(text, fg("green") + attr("bold"))
