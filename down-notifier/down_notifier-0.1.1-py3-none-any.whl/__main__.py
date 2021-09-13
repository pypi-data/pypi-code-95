import os
import sys

from down_notifier.checker import Checker
from down_notifier.parser import Parser


def main():
    if len(sys.argv) < 2:
        raise RuntimeError("argv < 2")
    filename = sys.argv[1]
    if not os.path.isfile(filename):
        raise RuntimeError(f"{filename} is not a file")

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    parser = Parser()
    sites = parser.parse(content)

    checker = Checker(sites)
    checker.start_loop()


if __name__ == "__main__":
    main()
