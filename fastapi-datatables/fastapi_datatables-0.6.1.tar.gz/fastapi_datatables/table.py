from __future__ import annotations

from typing import Callable, Iterator, TypeVar, Generic
from pydantic.generics import GenericModel
from pydantic import BaseModel


_T = TypeVar("_T")
_G = TypeVar("_G")


class DataTable(GenericModel, Generic[_T]):
    """Structure to hold the data the entire table."""

    page_size: int
    page_number: int
    num_pages: int
    total_results: int
    items: list[_T]

    class Config:
        arbitrary_types_allowed = True

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, num: int) -> _T:
        return self.items[num]

    def convert(self, converter: Callable[[_T], _G]) -> DataTable[_G]:
        """
        Convert all items of current model to new model using a converter function.

        For example, a pydantic.BaseModel can be used (it's constructor),
        or Model.from_orm to use pydantic from_orm function.
        """

        return DataTable(
            page_size=self.page_size,
            page_number=self.page_number,
            num_pages=self.num_pages,
            total_results=self.total_results,
            items=[converter(item) for item in self.items],
        )
