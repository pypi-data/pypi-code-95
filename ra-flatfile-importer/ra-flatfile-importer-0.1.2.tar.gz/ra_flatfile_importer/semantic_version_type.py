#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
import re
from functools import lru_cache
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterator
from typing import Pattern

from pydantic import BaseModel

# Regex from https://semver.org/
_semver_regex = (
    # Version part
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    # Prerelease part
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    # Build metadata
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


@lru_cache
def get_regex() -> Pattern:
    return re.compile(_semver_regex)


class SemanticVersion(str):
    @classmethod
    def __get_validators__(cls) -> Iterator[Callable]:
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: Dict) -> None:
        field_schema.update(
            pattern=_semver_regex,
            examples=["0.1.0", "1.0.0-alpha", "1.0.0-alpha+001"],
        )

    @classmethod
    def validate(cls, v: Any) -> "SemanticVersion":
        if not isinstance(v, str):
            raise TypeError("string required")
        m = get_regex().fullmatch(v)
        if not m:
            raise ValueError("invalid semver format")
        return cls(v)

    def __repr__(self) -> str:
        return f"SemanticVersion({super().__repr__()})"


class SemanticVersionModel(BaseModel):
    __root__: SemanticVersion
