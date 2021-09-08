import os
import typing

import attr

CoerceToString = typing.Union[os.PathLike[str], str]


@attr.dataclass(frozen=True)
class Token:
    pass


@attr.dataclass(frozen=True)
class Deleted(Token):
    path: str


Target = typing.Union[Token, str]
CoerceToTarget = typing.Union[Token, CoerceToString]


def deleted(path: CoerceToString) -> Target:
    return Deleted(os.fspath(path))


def coerce(target: CoerceToTarget) -> Target:
    if isinstance(target, Token):
        return target
    return os.fspath(target)
