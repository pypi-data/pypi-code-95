from __future__ import annotations

import pathlib
import typing

import attr
import pyrsistent


@attr.dataclass(frozen=True)
class Output:
    path: pathlib.Path
    names: pyrsistent.PVector[str] = pyrsistent.pvector()


@attr.dataclass(frozen=True)
class Input:
    path: pathlib.Path

    def as_output(self, *args: str) -> Output:
        return Output(self.path, pyrsistent.pvector(args))


IOType = typing.Union[Input, Output]

IO = Input, Output
