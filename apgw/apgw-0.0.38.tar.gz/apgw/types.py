"""Shared types."""
from typing import Any, List, Mapping, Optional, Tuple, Union

ConnectionArgs = Mapping[str, Any]

InsertAssignments = Union[
    Mapping[str, Any],
    List[Tuple[str, Any]],
]

LimitOffset = Tuple[Optional[int], Optional[int]]

Record = Mapping[str, Any]
Records = List[Record]
RecordsAndCount = Tuple[Records, int]

Params = List[Any]
SQL = Tuple[Optional[str], Params]
