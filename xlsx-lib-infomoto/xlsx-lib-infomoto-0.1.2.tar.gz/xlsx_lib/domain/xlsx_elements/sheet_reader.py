from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from domain.xlsx_elements.cell_position import CellPosition

# html_symbols: dict[str, str] = {
#     "º": "&#186;",
#     "Ω": "&#8486;",
# }
from modules.format_cell_value import format_cell_value


class SheetReader:
    def __init__(self, worksheet: Worksheet):
        self.worksheet: Worksheet = worksheet

    def read_cells_values(
            self,
            start_col: int,
            end_col: int,
            start_row: int,
            end_row: int,
    ) -> list[str]:
        values: list[str] = list()
        end_col += 1
        end_row += 1

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                values.append(format_cell_value(self.worksheet[CellPosition(col, row).position].value))

        return values

    def read_cell_value(
            self,
            col: int,
            row: int,
    ) -> str:
        return format_cell_value(self.worksheet[CellPosition(col, row).position].value)

    def read_cell(
            self,
            col: int,
            row: int,
    ) -> Cell:
        return self.worksheet[CellPosition(col, row).position]

    def read_cells(
            self,
            start_col: int,
            end_col: int,
            start_row: int,
            end_row: int,
    ) -> list[Cell]:
        cells: list[Cell] = list()
        end_col += 1
        end_row += 1

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                cells.append(self.worksheet[CellPosition(col, row).position])

        return cells
