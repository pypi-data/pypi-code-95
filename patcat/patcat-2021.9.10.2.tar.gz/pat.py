#!/usr/bin/env python3
from enum import IntEnum
from sys import argv, stdin, stderr
from string import whitespace

# These next 2 lines of code are only for ANSI escape support on Windows cmd/powershell
# If you do not use cmd/ps, you can comment them out or remove them
from os import system

system("")

# If the program is using too much memory, try decreasing this value
bytes_to_read = 1000000


class ColorInfo(IntEnum):
    AMOUNT = 299
    MAX_RGB_VALUE = 255
    PER_STAGE = (AMOUNT + 1) // 3
    MIN_RGB_VALUE = MAX_RGB_VALUE - PER_STAGE


if len(argv) == 1:
    argv.append("-")

for arg in argv[1:]:
    try:
        file = stdin if arg == "-" else open(arg, "r")
        read_result = file.read(bytes_to_read)
    except Exception as e:
        print(
            "Error "
            + (f"reading {file.name}" if "file" in globals() else "opening file")
            + f": {e}",
            file=stderr,
        )
        continue

    changes = len(list(filter(lambda c: not c in whitespace, read_result))) - 1

    step = 0 if changes == 0 else ColorInfo.AMOUNT / changes
    index = 0

    for char in read_result:
        if char in whitespace:
            print(char, end="")
            continue

        color_value = round(index)
        value_modifier = color_value % ColorInfo.PER_STAGE
        rgb_values = [
            ColorInfo.MIN_RGB_VALUE + value_modifier,
            ColorInfo.MAX_RGB_VALUE - value_modifier,
            ColorInfo.MIN_RGB_VALUE,
        ]
        [red, green, blue] = [
            [rgb_values[1], rgb_values[0], rgb_values[2]],
            rgb_values[::-1],
            [rgb_values[0], rgb_values[2], rgb_values[1]],
        ][color_value // ColorInfo.PER_STAGE]

        print("\x1b[38;2;%d;%d;%dm%s" % (red, green, blue, char), end="")
        index += step

    print("\x1b[0m")
