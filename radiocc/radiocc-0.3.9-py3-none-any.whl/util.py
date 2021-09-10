#!/usr/bin/env python3

"""
Toolbox.
"""

import enum
from pathlib import Path
from typing import Generator, List, Optional

from pudb import set_trace as bp  # noqa


class AutoEnum(enum.Enum):
    def _generate_next_value_(  # type: ignore
        name: str, start: int, count: int, last_values: List[str]
    ) -> str:
        return name


def directories(
    PATH: Path, FILTER: Optional[str] = None
) -> Generator[Path, None, None]:
    """Iterate over the directories of a given path."""
    if FILTER is None:
        FILTER = "*"
    return (P for P in PATH.glob(FILTER) if P.is_dir())
