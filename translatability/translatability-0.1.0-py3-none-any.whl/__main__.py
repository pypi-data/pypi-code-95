import os
import sys
from .tools.manage import execute_from_command_line


def main():
    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        print(e)
        raise Exception(
            "Something went wrong "
            "when trying to execute "
            "the requested command(s)."
        )


if __name__ == "__main__":
    main()
