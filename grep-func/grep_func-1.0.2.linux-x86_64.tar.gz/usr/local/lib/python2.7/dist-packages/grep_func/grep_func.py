import re
from inspect import getmembers, isfunction, ismethod
from colorama import Fore


def grep_func(module, pattern):
    matching = [
        member[0]
        for member in getmembers(
            module, predicate=lambda x: isfunction(x) or ismethod(x)
        )
        if re.search(pattern, member[0])
    ]

    # Print grep style
    for match in matching:
        print(re.sub(r"({})".format(pattern), Fore.RED + r"\1" + Fore.RESET, match))
