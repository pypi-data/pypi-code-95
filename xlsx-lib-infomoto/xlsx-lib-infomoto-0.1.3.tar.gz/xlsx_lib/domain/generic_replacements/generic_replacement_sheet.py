from typing import Optional

from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from domain.generic_replacements.replacement import Replacement
from domain.generic_replacements.replacement_part import ReplacementPart

from domain.xlsx_elements.sheet import Sheet


class GenericReplacementsSheet(Sheet):
    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet=worksheet)

    def get_generic_replacements(
            self,
            start_col: int = 1,
            start_row: int = 2,
    ) -> list[Replacement]:
        row_index = start_row

        replacements: list[Replacement] = list[Replacement]()
        actual_replacement: Optional[Replacement] = None
        already_none: bool = False

        while True:
            cell: Cell = self.sheet_reader.read_cell(start_col, row_index)

            if cell.value is None:
                if already_none:
                    replacements.append(actual_replacement)
                    break

                already_none = True
            else:
                already_none = False
                if cell.font.b:
                    if actual_replacement is not None:
                        replacements.append(actual_replacement)
                    actual_replacement = self.get_replacement(start_col, row_index)
                else:
                    actual_replacement.parts.append(
                        self.get_replacement_detail(start_col, row_index)
                    )

            row_index += 1

        return replacements

    def get_replacement_detail(
            self,
            col: int,
            row: int
    ) -> ReplacementPart:
        values: list[str] = self.sheet_reader.read_cells_values(col, 3, row, row + 1)

        return ReplacementPart(
            name=values[0],
            reference=values[1],
            observations=values[2],
        )

    def get_replacement(
            self,
            col: int,
            row: int
    ) -> Replacement:
        values: list[str] = self.sheet_reader.read_cells_values(col, 3, row, row + 1)

        return Replacement(
            name=values[0],
            reference=values[1],
            observations=values[2],
        )
