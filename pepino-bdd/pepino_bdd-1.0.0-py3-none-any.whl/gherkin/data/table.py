from typing import List
from ..location import GherkinLocation
from ...data import DataTableCell, DataTableRow, DataTable


class GherkinDataTableCell(GherkinLocation, DataTableCell):
    """Gherkin Implementation of DataTable Cell."""

    def __init__(self, parsed):
        super(GherkinDataTableCell, self).__init__(parsed)
        self._value = parsed["value"]

    @property
    def value(self) -> str:
        return self._value


class GherkinDataTableRow(GherkinLocation, DataTableRow):
    """Gherkin implementation of DataTable row."""

    def __init__(self, parsed):
        super(GherkinDataTableRow, self).__init__(parsed)
        self._cells = [GherkinDataTableCell(cell) for cell in parsed["cells"]]

    @property
    def cells(self) -> List[DataTableCell]:
        return self._cells


class GherkinDataTable(GherkinLocation, DataTable):
    """Gherkin implentation of DataTable."""

    def __init__(self, parsed):
        super(GherkinDataTable, self).__init__(parsed)
        self._rows = [GherkinDataTableRow(row) for row in parsed["rows"]]

    @property
    def rows(self) -> List[DataTableRow]:
        return self._rows
