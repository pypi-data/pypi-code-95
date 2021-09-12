from typing import List, Optional

from emoji import emojize
from termcolor import colored


def mirror_ends(string: str, ends: List[str]) -> str:
    """
    >>> mirror_ends('abc', ['x', '-'])
    'x - abc - x'
    """
    return " ".join([*ends, string, *reversed(ends)])


def heading(string: str, step: List[int], emoji: str) -> str:
    return " ".join(
        [
            f"[{'/'.join([str(i) for i in step])}]",
            emojize(f":{emoji}:"),
            colored(string, "green"),
        ]
    )


def notice(string: str, emoji: Optional[List[str]] = None) -> str:
    return colored(
        mirror_ends(
            string,
            [emojize(f":{i}:") for i in emoji] if emoji is not None else [],
        ),
        "blue",
    )


def progress(string: str) -> str:
    return colored(string, "cyan")


def dry_run(string: str) -> str:
    return emojize(f":test_tube: Dry run: {string}")
