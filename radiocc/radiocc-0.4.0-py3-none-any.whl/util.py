#!/usr/bin/env python3

"""
Toolbox.
"""

import enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

import yaml
from colored import attr, fg
from pudb import set_trace as bp  # noqa


class AutoEnum(enum.Enum):
    def _generate_next_value_(  # type: ignore
        name: str, start: int, count: int, last_values: List[str]
    ) -> str:
        return name


class GetAttributes:
    def get_attributes(self) -> Dict[str, Any]:
        return {
            attribute: self.__getattribute__(attribute)
            for attribute in self.__dir__()
            if not attribute.startswith("__")
            and not callable(self.__getattribute__(attribute))
        }


def directories(
    PATH: Path, FILTER: Optional[str] = None
) -> Generator[Path, None, None]:
    """Iterate over the directories of a given path."""
    if FILTER is None:
        FILTER = "*"
    return (P for P in PATH.glob(FILTER) if P.is_dir())


def format_info(message: str) -> str:
    """Format an info message."""
    return f"{fg('yellow')}{message}{attr(0)}"


def format_validation(message: str) -> str:
    """Format a validation message."""
    return f"{fg('green')}{message}{attr(0)}"


def format_error(message: str) -> str:
    """Format an error message."""
    return f"{fg('red')}Error: {message}{attr(0)}"


def print_info(message: str) -> None:
    """Print an info message with a template format."""
    print(format_info(message))


def print_validation(message: str) -> None:
    """Print a validation message with a template format."""
    print(format_validation(message))


def print_error(message: str) -> None:
    """Print an error message with a template format."""
    print(format_error(message))


def raise_error(message: str) -> None:
    """Raise an error with a template format."""
    raise SystemExit(NotImplementedError(format_error(message)))


def form_yes_or_no(question: str, default_no: bool = True) -> bool:
    """
    Single yes or no question without recursion.

    Credit:
        Inspired from
        @icamys commented on 29 Nov 2020 on Github,
        https://gist.github.com/garrettdreyfus/8153571
    """
    choices = " [y/N]: " if default_no else " [Y/n]: "
    default_answer = "n" if default_no else "y"
    reply = str(input(question + choices)).lower().strip() or default_answer
    if reply[:1] == "y":
        return True
    elif reply[:1] == "n":
        return False
    else:
        return not default_no


def yaml_represent_none(self: Any, _: Any) -> Any:
    return self.represent_scalar("tag:yaml.org,2002:null", "")


def yaml_add_representer_none() -> None:
    yaml.add_representer(type(None), yaml_represent_none)
