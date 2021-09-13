import abc
from functools import partial
from typing import (
    Callable,
    List,
    Dict,
    Iterable,
    Union,
    TypeVar,
    Type,
    cast,
    get_args,
    get_origin,
)

from ..registry import registry

from ..exceptions import CucumberTableException

T = TypeVar("T")
Ti = TypeVar("Ti")


class DataTableCell(abc.ABC):
    """DataTable cell for Cucumber."""

    @abc.abstractproperty
    def value(self) -> str:
        """Value of this cell."""
        ...


class DataTableRow(metaclass=abc.ABCMeta):
    """DataTable row for cucumber."""

    @abc.abstractproperty
    def cells(self) -> List[DataTableCell]:
        """Cells for this row."""
        ...


class DataTable(metaclass=abc.ABCMeta):
    """Datatable for cucumber."""

    @abc.abstractproperty
    def rows(self) -> List[DataTableRow]:
        """Rows of this table."""
        ...

    def column(self, column: Union[str, int]) -> List[str]:
        """
        Get the values of a column of the Datatable.

        Args:
            column (Union[str, int]): Name or index of the column

        Raises:
            CucumberTableException: If column is invalid

        Returns:
            List[str]: List of values for the requested column
        """
        startrow = 0
        if isinstance(column, str):
            for idx, cell in enumerate(self.rows[0].cells):
                startrow = 1
                if cell.value == column:
                    colno = idx
                    break
            else:
                raise CucumberTableException(self, f"No column called {column}")
        else:
            if column >= len(self.rows[0].cells) or column < 0:
                raise CucumberTableException(self, f"No column for index {column}")
            colno = column
        return [row.cells[colno].value for row in self.rows[startrow:]]

    def row(self, rowno: int) -> List[str]:
        """
        Get the values of a row of the DataTable.

        Args:
            rowno (int): index of row

        Raises:
            CucumberTableException: If rowno is invalid

        Returns:
            List[str]: List of values for the requested row
        """
        if rowno >= len(self.rows) or rowno < 0:
            raise CucumberTableException(self, f"No row for index {rowno}")
        return [cell.value for cell in self.rows[rowno].cells]

    def _list(self, iterable: Iterable, key_func: Callable) -> List:
        return [key_func(v) for v in iterable]

    def _dict(
        self, iterable: Iterable, key_func: Callable, value_func: Callable
    ) -> Dict:
        return {key_func(v): value_func(v) for v in iterable}

    def _inner_value(self, value, inside_type: Type[Ti]) -> Ti:
        if (
            get_origin(inside_type) is dict
            and isinstance(value, list)
            and len(value) > 1
        ):

            key_type, value_type = get_args(inside_type)
            return cast(
                Ti,
                self._dict(
                    [value],
                    lambda item: key_type(item[0]),
                    lambda item: partial(self._inner_value, inside_type=value_type)(
                        item[1:]
                    ),
                ),
            )
        if get_origin(inside_type) is list and isinstance(value, list):
            (l_type,) = get_args(inside_type)
            return cast(
                Ti,
                self._list(
                    (v for v in value), partial(self._inner_value, inside_type=l_type)
                ),
            )
        if isinstance(value, list):
            try:
                return registry.get_type_func(inside_type)(*value)
            except Exception:
                return registry.get_type_func(inside_type)(value[0])  # type: ignore
        return registry.get_type_func(inside_type)(value)  # type: ignore

    def convert(self, column_based: bool, convert_to: Type[T]) -> T:
        """
        Convert the table to the tpe specified

        Args:
            column_based (bool): Wetherthe Table is a list of column based values or row based values
            convert_to (Type[T]): Return Type

        Returns:
            T: Requested Type
        """
        if column_based:
            if get_origin(convert_to) is dict:
                key_type, value_type = get_args(convert_to)
                return cast(
                    T,
                    self._dict(
                        range(len(self.rows)),
                        lambda k: key_type(self.rows[0].cells[k].value),
                        lambda v: self._inner_value(self.column(v)[1:], value_type),
                    ),
                )
            if get_origin(convert_to) is list:
                (inside_type,) = get_args(convert_to)
                return cast(
                    T,
                    self._list(
                        (self.column(i) for i in range(len(self.rows))),
                        partial(self._inner_value, inside_type=inside_type),
                    ),
                )
            try:
                return registry.get_type_func(convert_to)(*self.column(0))  # type: ignore
            except Exception:
                return registry.get_type_func(convert_to)(self.column(0)[0])
        if get_origin(convert_to) is dict:
            key_type, value_type = get_args(convert_to)
            return cast(
                T,
                self._dict(
                    range(len(self.column(0))),
                    lambda k: key_type(self.column(0)[k]),
                    lambda v: self._inner_value(
                        [cell.value for cell in self.rows[v].cells[1:]], value_type
                    ),
                ),
            )
        if get_origin(convert_to) is list:
            (inside_type,) = get_args(convert_to)
            return cast(
                T,
                self._list(
                    (
                        [cell.value for cell in self.rows[i].cells]
                        for i in range(len(self.column(0)))
                    ),
                    partial(self._inner_value, inside_type=inside_type),
                ),
            )
        try:
            return registry.get_type_func(convert_to)(*[cell.value for cell in self.rows[0].cells])
        except Exception:
            return registry.get_type_func(convert_to)(self.rows[0].cells[0].value)
