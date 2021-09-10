"""Contains constraint data structures and types."""
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, List, Union

from apgw.types import Params


@dataclass(frozen=True)
class BinaryConstraint:
    column: str
    value: Any
    operator: str = "="


@dataclass(frozen=True)
class TextConstraint:
    sql: str
    params: Params


class DictConstraint(OrderedDict):
    """An alias for OrderedDict."""


@dataclass(frozen=True)
class Literal:
    value: str


@dataclass(frozen=True)
class GroupConstraint:
    """Represents a group of constraints."""

    joiner: str
    constraints: List[Union["GroupConstraint", BinaryConstraint]]

    def add(self, constraint: Union["GroupConstraint", BinaryConstraint]):
        self.constraints.append(constraint)


Assignments = Union[
    BinaryConstraint,
    DictConstraint,
    List[BinaryConstraint],
    TextConstraint,
]

Constraints = Union[
    Assignments,
    GroupConstraint,
]
