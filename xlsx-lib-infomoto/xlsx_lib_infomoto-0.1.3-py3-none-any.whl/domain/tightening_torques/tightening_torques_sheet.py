from typing import Optional

from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from domain.tightening_torques.component import Component
from domain.tightening_torques.component_part import ComponentPart
from domain.tightening_torques.component_part_screw import ComponentPartScrew
from domain.tightening_torques.tightening_torque_step import TighteningTorqueStep
from domain.xlsx_elements.sheet import Sheet


class TighteningTorquesSheet(Sheet):
    def __init__(self, worksheet: Worksheet):
        super().__init__(worksheet=worksheet)

    def get_components_screws_tightening_torques(
            self,
            start_col: int = 0,
            start_row: int = 2,
    ) -> list[Component]:
        row_index = start_row

        components: list[Component] = list()

        while True:
            cell: Cell = self.sheet_reader.read_cell(start_col, row_index)

            if cell.value is None:
                values = self.sheet_reader.read_cells_values(
                    start_col=start_col,
                    end_col=start_col,
                    start_row=row_index+1,
                    end_row=row_index+4,
                )

                matches: list[str] = [value for value in values if value is not None]

                if len(matches) == 0:
                    break
                elif len(components[-1].parts[-1].screws[-1].steps) > 0:
                    tightening_torque_step = self.get_tightening_torque_step(start_col, row_index)

                    if tightening_torque_step.name is not None or tightening_torque_step.tightening_torque is not None:
                        components[-1].parts[-1].screws[-1].steps.append(tightening_torque_step)

                    row_index += 1
                    continue
                else:
                    row_index += 1
                    continue

            if cell.font.b and cell.alignment.horizontal == "right":
                components.append(self.get_component(start_col, row_index))

            elif cell.font.b and cell.alignment.horizontal == "center":
                components[-1].parts.append(self.get_component_part(start_col, row_index))

            elif cell.alignment.horizontal in ["left", "general", None]:
                components[-1].parts[-1].screws.append(self.get_component_part_screws(start_col, row_index))

            elif cell.alignment.horizontal == "right":
                components[-1].parts[-1].screws[-1].steps.append(self.get_tightening_torque_step(start_col, row_index))

            row_index += 1

        return components

    def get_component(
            self,
            col: int,
            row: int
    ) -> Component:
        return Component(
            name=self.sheet_reader.read_cell_value(col, row)
        )

    def get_component_part(
            self,
            col: int,
            row: int
    ) -> ComponentPart:
        return ComponentPart(
            name=self.sheet_reader.read_cell_value(col, row)
        )

    def get_component_part_screws(
            self,
            col: int,
            row: int
    ) -> ComponentPartScrew:
        values: list[str] = self.sheet_reader.read_cells_values(col, col+1, row, row)

        tightening_torque: str = values[1]

        detail: Optional[str] = None
        if tightening_torque is not None and tightening_torque.endswith("*"):
            detail = self.sheet_reader.read_cell_value(col, row + 1)

        return ComponentPartScrew(
            name=values[0],
            tightening_torque=tightening_torque,
            detail=detail,
        )

    def get_tightening_torque_step(
            self,
            col: int,
            row: int
    ) -> TighteningTorqueStep:
        values: list[str] = self.sheet_reader.read_cells_values(col, col + 1, row, row)

        return TighteningTorqueStep(
            name=values[0],
            tightening_torque=values[1],
        )
