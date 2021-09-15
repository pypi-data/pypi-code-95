import os
from pathlib import Path
from typing import Iterator, Optional


def maybe(m, key):
    if m is None:
        return None
    return m.get(key)


def merge(acc, piece):
    if not isinstance(acc, dict):
        return piece
    for (key, value) in piece.items():
        if key not in acc:
            acc[key] = value
        else:
            acc[key] = merge(acc[key], piece[key])
    return acc


def parents(path: Optional[Path] = None) -> Iterator[Path]:
    path = path or Path(os.getcwd())
    parts = path.parts
    current = Path(parts[0])
    yield current
    for part in parts[1:]:
        current = current.joinpath(part)
        yield current
