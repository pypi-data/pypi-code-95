from __future__ import annotations
from abc import abstractmethod
from fastapi_datatables.filtration import FiltrationData
from fastapi import Depends

from pydantic import BaseModel
from typing import Callable, Iterable, Iterator, get_type_hints, Union, Any, Optional

from .query import get_filtration, WILDCARD_PARAMETER


class FieldsView:
    def __init__(self, items: set[str]) -> None:
        self._items = items

    def __rmatmul__(self, other: Union[str, Any]) -> FieldsView:
        if isinstance(other, str):
            return FieldsView(
                {f"{other}.{item.split('.')[-1]}" for item in self._items}
            )
        return NotImplemented

    def __add__(self, other: Union[FieldsView, Any]) -> FieldsView:
        if isinstance(other, FieldsView):
            return FieldsView(self._items | other._items)
        return NotImplemented

    def __str__(self) -> str:
        return f"FieldsView({', '.join(sorted(self._items))})"

    def __iter__(self) -> Iterator[str]:
        # First is wildcard
        # Then columns without table
        # Then other columns
        return iter(
            sorted(
                self._items,
                key=lambda field: (field != WILDCARD_PARAMETER, "." in field, field),
            )
        )

    __repr__ = __str__


class Filterable:
    @classmethod
    def fields(cls, table_name: Optional[str] = None) -> FieldsView:
        res = FieldsView(set(get_type_hints(cls)) - cls.__ignore_fields__())
        if table_name is None:
            return res
        return table_name @ res

    @classmethod
    def filter(cls) -> Callable[..., FiltrationData]:
        return get_filtration(cls.fields())

    @classmethod
    def __ignore_fields__(cls) -> set[str]:
        return set()


def Filter(f: Filterable) -> FiltrationData:
    return Depends(f.filter())