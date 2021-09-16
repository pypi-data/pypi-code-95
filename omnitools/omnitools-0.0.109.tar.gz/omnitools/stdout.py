import sys
from typing import *


__ALL__ = ["p"]


def p(*args, end="\n") -> None:
    print(*args, end=end, flush=True)


