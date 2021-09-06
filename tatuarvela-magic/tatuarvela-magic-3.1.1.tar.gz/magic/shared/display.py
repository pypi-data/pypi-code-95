import sys
from enum import Enum

# Emoji spacing in terminal is unpredictable
# These extra spaces appear to fix issues
EMOJI_FAILURE = "\u274c\ufeff"
EMOJI_FIRE = "\U0001f525"
EMOJI_SPARKLE = "\u2728\ufeff"
EMOJI_SUCCESS = "\u2705\ufeff"
EMOJI_TIMER = "\u23f1\u0020"
EMOJI_TRASH = "\U0001f5d1\u0020"
EMOJI_WIZARD = "\U0001f9d9"


class Color(Enum):
    BLACK = "\u001b[30m"
    RED = "\u001b[31m"
    GREEN = "\u001b[32m"
    YELLOW = "\u001b[33m"
    BLUE = "\u001b[34m"
    MAGENTA = "\u001b[35m"
    CYAN = "\u001b[36m"
    WHITE = "\u001b[37m"


RESET_COLOR = "\u001b[0m"


def in_color(text, color: Color):
    return f"{color.value}{text}{RESET_COLOR}"


def print_error(error):
    print(f"""{in_color(f'{EMOJI_FIRE} Error: {error}', Color.RED)}""")


def clear_last_line():
    sys.stdout.write("\033[F")  # back to previous line
    sys.stdout.write("\033[K")  # clear line
