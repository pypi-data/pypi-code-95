from abc import ABC
from typing import List

import pandas as pd
from ipyaggrid import Grid
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from magnumapi.geometry.Area import Area
from magnumapi.geometry.Block import Block
from magnumapi.geometry.Line import Line


class Geometry(ABC):
    """ Abstract geometry class providing a skeleton for all geometry types (CosTheta, Rectangular, etc.).

    """
    def __init__(self, blocks: List[Block]) -> None:
        """ Constructor of a Geometry class

        :param blocks: a list of instances of Block class implementations (e.g., RectangularBlock, CosThetaBlock, etc.)
        """
        self.blocks = blocks

    def build_blocks(self) -> None:
        """ Method building all blocks for a given geometry definition

        """
        for block in self.blocks:
            block.build_block()

    def to_roxie_df(self) -> pd.DataFrame:
        """ Method concatenates row definition of each block into a ROXIE-compatible dataframe

        :return: a concatenated dataframe with ROXIE block definition for a geometry instance
        """
        return pd.concat([block.to_roxie_df() for block in self.blocks], axis=0).reset_index(drop=True)

    def to_df(self) -> pd.DataFrame:
        """ Method concatenating dataframes with area coordinates for each block

        :return: a concatenated dataframe with area coordinates
        """
        return pd.concat([block.to_df() for block in self.blocks], axis=0).reset_index(drop=True)

    def plot_blocks(self, figsize=(10, 10), is_grid=True, xlim=(0, 80), ylim=(0, 80)) -> None:
        """ Method plotting all blocks with matplotlib library

        :param figsize: size of a figure on a screen
        :param is_grid: if True, then the grid is displayed, otherwise False
        :param xlim: limits in x-direction
        :param ylim: limits in y-direction
        """
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.grid(is_grid)

        for block in self.blocks:
            block.plot_block(ax)

        plt.show()

    def plotly_blocks(self, figsize=(65, 65), xlim=(0, 80), ylim=(0, 80)) -> None:
        """ Method plotting blocks with plotly library

        :param figsize: size of the figure on a display
        :param xlim: limits in x-direction
        :param ylim: limits in y-direction
        """
        go_scatters = Geometry.create_plotly_scatters(self.blocks)

        fig = go.Figure(go_scatters)
        fig.update_layout(
            autosize=False,
            width=750,
            height=750,
            yaxis_range=ylim,
            xaxis_range=xlim,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig.add_trace(px.scatter(x=[0], y=[0]).data[0])
        fig.update_xaxes(title=dict(text='x, [mm]'))
        fig.update_yaxes(title=dict(text='y, [mm]'))
        fig.show()

    @staticmethod
    def create_plotly_scatters(blocks: List[Block]) -> List[go.Scatter]:
        """ Static method creating a list of plotly scatter instances

        :param blocks: list of blocks to convert to plotly scatter
        :return: a list of plotly scatter instances
        """
        go_scatter = []
        index = 1
        for block in blocks:
            for area in block.areas:
                x = []
                y = []
                for i in range(4):
                    x.append(area.get_line(i).p1.x)
                    y.append(area.get_line(i).p1.y)

                x.append(area.get_line(0).p1.x)
                y.append(area.get_line(0).p1.y)

                go_scatter.append(go.Scatter(x=x, y=y, fill="toself", fillcolor='white', marker=dict(size=1),
                                             name='turn' + str(index), line=go.scatter.Line(color='blue')))
                index += 1
        return go_scatter

    def plot_bare_blocks(self, figsize=(15, 15), is_grid=True, xlim=(0, 80), ylim=(0, 80)) -> None:
        """ Method plotting bare (uninsulated) areas for all blocks in a geometry

        :param figsize: size of a figure on a screen
        :param is_grid: if True, then the grid is displayed, otherwise False
        :param xlim: limits in x-direction
        :param ylim: limits in y-direction
        """
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_aspect('equal', 'box')
        ax.grid(is_grid)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        for block in self.blocks:
            block.plot_bare_block(ax)

        plt.show()

    def get_bare_areas_for_blocks(self) -> List[List[Area]]:
        """ Method returning a list of list of bare (uninsulated) areas constructed from iterating over all blocks in a
        geometry and all areas in a block.

        :return: a list of list of bare (uninsulated) areas
        """
        return [block.get_bare_areas() for block in self.blocks]

    def is_outside_of_first_quadrant(self, eps=1e-30) -> True:
        """ Method checking whether a geometry is fully positioned in the first quadrant.

        :param eps: a machine precision for comparison of 0 value
        :return: True if an Area instance is in the first quadrant, False otherwise
        """
        # ToDo: Would require an adjustment once layers are introduced.
        for block in self.blocks:
            if block.is_outside_of_first_quadrant(eps=eps):
                return True

        return False

    def are_turns_overlapping(self) -> bool:
        """Method checking whether turns from neighbouring blocks are overlapping.

        :return: True, if at least two neighbouring turns are overlapping, otherwise False
        """
        radius_prev = None
        for index, block in enumerate(self.blocks):
            # ToDo Fixed once layers are implemented
            if radius_prev == block.block_def.radius:
                area_curr = block.areas[0]
                area_prev = self.blocks[index - 1].areas[-1]
                line_prev = area_prev.get_line(2)
                line_prev_rev = Line.of_end_points(line_prev.p2, line_prev.p1)
                orient_p1 = Line.calculate_point_orientation_wrt_line(line_prev_rev, area_curr.get_line(0).p1)
                orient_p2 = Line.calculate_point_orientation_wrt_line(line_prev_rev, area_curr.get_line(0).p2)

                if orient_p1 == -1 or orient_p2 == -1:
                    return True

            radius_prev = block.block_def.radius

        return False

    def is_wedge_tip_too_sharp(self, min_value_in_mm: float) -> bool:
        """ Method checking whether wedge tip is too sharp. Method computes the wedge tip arc length, by finding an
        intersection of two neighbouring turns with an inner radius

        :param min_value_in_mm: minimum value of  the wedge tip arc
        :return: True if wedge length is below the minimum value
        """
        radius_prev = None
        for index, block in enumerate(self.blocks):
            # ToDo Fixed once layers are implemented
            if radius_prev == block.block_def.radius:
                area_curr = block.areas[0]
                area_prev = self.blocks[index - 1].areas[-1]

                line_first_area = area_curr.get_line(0)
                line_last_area = area_prev.get_line(2)

                l_arc = Line.calc_arc_length_between_two_lines(block.block_def.radius, line_last_area, line_first_area)
                if l_arc < min_value_in_mm:
                    return True

            radius_prev = block.block_def.radius

        return False

    @staticmethod
    def display_definition_table(df: pd.DataFrame) -> Grid:
        """ Static method displaying a definition table in an editable format in a notebook

        :param df: a dataframe to be displayed
        :return: an object to be displayed in a notebook
        """
        column_defs = [{'headername': c, 'field': c} for c in df.columns]

        grid_options = {
            'columnDefs': column_defs,
            'enableSorting': True,
            'enableFilter': True,
            'enableColResize': True,
            'enableRangeSelection': True,
            'rowSelection': 'multiple',
        }

        return Grid(grid_data=df,
                    grid_options=grid_options,
                    quick_filter=True,
                    show_toggle_edit=True,
                    sync_on_edit=True,
                    export_csv=True,
                    export_excel=True,
                    theme='ag-theme-balham',
                    show_toggle_delete=True,
                    columns_fit='auto',
                    index=False)
