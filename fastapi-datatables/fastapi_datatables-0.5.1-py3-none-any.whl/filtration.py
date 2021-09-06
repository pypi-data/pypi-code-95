from __future__ import annotations

from typing import Optional, Literal, Union, TypedDict, Any, overload
from .operations import FiltrationOperator
from pydantic import BaseModel, validator, Field
from sqlalchemy.orm import Query
from sqlalchemy_filters import apply_filters, apply_sort, apply_pagination
from .table import DataTable


class FilterSpec(TypedDict, total=False):
    model: Optional[str]
    field: str
    op: str
    value: str


class RawFilterSpec(TypedDict):
    field: str
    op: Union[FiltrationOperator, str]
    value: str


AnyFilterSpec = Union[RawFilterSpec, FilterSpec]


class SortSpec(TypedDict):
    field: str
    direction: str


class ModelSortSpec(SortSpec):
    model: str


def _split_field(field: str) -> dict[str, str]:
    # The field can name the model explicitly like
    # Model.field
    # Otherways the default main model will be used
    if "." in field:
        if field.count(".") > 1:
            raise ValueError("In field can only be one `.`")

        table, field = field.split(".")
        return {"model": table, "field": field}
    else:
        return {"field": field}


class ParsingData:
    _or: list[FilterSpec]
    _and: list[FilterSpec]

    def __init__(
        self,
        json: dict[str, FilterSpec] = {},
        *,
        _or: Union[list[RawFilterSpec], list[FilterSpec]] = [],  # type: ignore
        _and: Union[list[RawFilterSpec], list[FilterSpec]] = [],  # type: ignore
    ) -> None:
        self._or = json.get("or", []) + [ParsingData.__convert_raw(e) for e in _or]  # type: ignore
        self._and = json.get("and", []) + [ParsingData.__convert_raw(e) for e in _and]  # type: ignore

    def to_spec(self) -> dict[str, list[FilterSpec]]:
        res: dict[str, list[FilterSpec]] = {}
        if self._or != []:
            res |= {"or": self._or}
        if self._and != []:
            res |= {"and": self._and}
        return res

    @staticmethod
    def __convert_raw(raw: AnyFilterSpec) -> FilterSpec:
        op = raw["op"]
        if isinstance(op, FiltrationOperator):
            op = str(op.value)

        if "model" in raw:
            return {
                "model": raw["model"],  # type: ignore
                "field": raw["field"],
                "op": op,
                "value": raw["value"],
            }
        else:
            return _split_field(raw["field"]) | {  # type: ignore
                "op": op,
                "value": raw["value"],
            }

    def copy(self) -> ParsingData:
        """ Return the shallow copy of ParsingData object. """

        return ParsingData(_or=self._or.copy(), _and=self._and.copy())

    @staticmethod
    def from_dict(data: FilterSpec) -> ParsingData:
        return ParsingData(_and=[data])

    @staticmethod
    def disjunction(data: list[FilterSpec] = []) -> ParsingData:
        """ Construct ParsingData using a logical or. """
        return ParsingData(_or=data)

    @staticmethod
    def conjunction(data: list[FilterSpec] = []) -> ParsingData:
        """ Construct ParsingData using a logical and. """
        return ParsingData(_and=data)

    @staticmethod
    def __get_spec_field(spec: FilterSpec) -> str:
        return f"{spec['model']}.{spec['field']}" if "model" in spec else spec["field"]

    def __add__(self, other: Union[ParsingData, FilterSpec]) -> ParsingData:
        if isinstance(other, dict):
            other = ParsingData.from_dict(other)
        result = self.copy()
        result._and.extend(other._and)
        result._or.extend(other._or)
        return result

    def __getitem__(self, key: str) -> set[tuple[FiltrationOperator, str]]:
        return {
            (FiltrationOperator(spec["op"]), spec["value"])
            for spec in self._and
            if self.__get_spec_field(spec) == key
        }

    def __contains__(self, item: str) -> bool:
        return any(item == self.__get_spec_field(spec) for spec in self._and)


class FiltrationData(BaseModel):
    to_filter: ParsingData = ParsingData()
    page_number: int = 1
    page_size: int = Field(
        default_factory=lambda: FiltrationData.__get_default("page_size")
    )
    order_by: Optional[str] = Field(
        default_factory=lambda: FiltrationData.__get_default("order_by")
    )
    sort_by: Literal["asc", "desc"] = Field(
        default_factory=lambda: FiltrationData.__get_default("sort_by")
    )

    class Config:
        arbitrary_types_allowed = True

    _default = {"page_size": 10, "order_by": None, "sort_by": "asc"}

    @classmethod
    def __get_default(cls, field: str) -> Any:
        return cls._default[field]

    @classmethod
    @overload
    def set_default(cls, attr: Literal["page_size"], value: int) -> None:
        ...

    @classmethod
    @overload
    def set_default(cls, attr: Literal["order_by"], value: Optional[str]) -> None:
        ...

    @classmethod
    @overload
    def set_default(
        cls, attr: Literal["sort_by"], value: Literal["asc", "desc"]
    ) -> None:
        ...

    @classmethod
    def set_default(cls, attr, value):
        cls._default[attr] = value

    @classmethod
    @validator("page_size", pre=True, always=True)
    def _pre_validate_page_size(cls, page_size: Optional[int]) -> int:
        print("page_size")
        return page_size or cls.__get_default("page_size")

    @classmethod
    @validator("order_by", pre=True, always=True)
    def _pre_validate_order_by(cls, order_by: Optional[str]) -> Optional[str]:
        print("order_by")
        return order_by or cls.__get_default("order_by")

    @classmethod
    @validator("sort_by", pre=True, always=True)
    def _pre_validate_sort_by(
        cls, sort_by: Optional[Literal["asc", "desc"]]
    ) -> Literal["asc", "desc"]:
        print("sort_by")
        return sort_by or cls.__get_default("sort_by")

    def __get_sort_spec(self) -> list[ModelSortSpec]:
        return [_split_field(self.order_by) | {"direction": self.sort_by}]  # type: ignore

    def apply(self, query: Query) -> DataTable:
        filter_spec = self.to_filter.to_spec()
        if filter_spec != {}:
            query = apply_filters(query, filter_spec)

        if self.order_by is not None:
            sort_spec = self.__get_sort_spec()
            query = apply_sort(query, sort_spec)

        query, pagination = apply_pagination(
            query, page_number=self.page_number, page_size=self.page_size
        )
        page_size, page_number, num_pages, total_results = pagination

        return DataTable(
            page_size=page_size,
            page_number=page_number,
            num_pages=num_pages,
            total_results=total_results,
            items=query.all(),
        )

    def filter(
        self,
        field: str,
        value: str,
        operator: Union[FiltrationOperator, str] = FiltrationOperator.EQUAL,
    ) -> FiltrationData:
        if isinstance(operator, str):
            operator = FiltrationOperator(operator)

        spec: FilterSpec = {
            "field": field,
            "value": value,
            "op": operator.value,
        }

        self.to_filter += spec
        return self