from looqbox.objects.table_json_generator import TableJson
from looqbox.objects.table_json_generator import cel_to_column
from looqbox.objects.looq_object import LooqObject
from looqbox.objects.table_cell import TableCell
from collections import defaultdict, OrderedDict
import pandas as pd
import numpy as np
import json
import types


class TableBody(LooqObject):

    def __init__(self,
                 table_content=None,
                 value_link=None,
                 value_style=None,
                 value_class=None,
                 value_tooltip=None,
                 value_format=None,
                 row_link=None,
                 row_style=None,
                 row_class=None,
                 row_tooltip=None,
                 row_format=None,
                 row_range=None,
                 col_link=None,
                 col_style=None,
                 col_class=None,
                 col_tooltip=None,
                 col_format=None,
                 col_range=None,
                 null_as=None):

        super().__init__()
        self.data = table_content
        self.value_link = value_link
        self.value_style = value_style
        self.value_class = value_class
        self.value_tooltip = value_tooltip
        self.value_format = value_format
        self.row_link = row_link
        self.row_style = row_style
        self.row_class = row_class
        self.row_tooltip = row_tooltip
        self.row_format = row_format
        self.row_range = row_range
        self.col_link = col_link
        self.col_style = col_style
        self.col_class = col_class
        self.col_tooltip = col_tooltip
        self.col_format = col_format
        self.col_range = col_range
        self.null_as = null_as

    @property
    def to_json_structure(self):
        """
        Generate the json that will be add in the ObjectTable body part.

        :return: body_json: Dictionary that will be converted to a JSON inside the looq_table function.

        """

        table_data = self.data
        if isinstance(table_data, pd.DataFrame):
            table_data = table_data.replace({np.nan: None})
            table_data.fillna(self.null_as, inplace=True)
            table_data = table_data.to_dict('records')

        if table_data is None:
            return None

        ColumnGenerator = TableJson(data=self.data,
                                    cell_style=self.col_style,
                                    cell_class=self.col_class,
                                    cell_link=self.col_link,
                                    cell_format=self.col_format,
                                    cell_tooltip=self.col_tooltip)

        CellGenerator = TableJson(data=self.data,
                                  cell_style=self.value_style,
                                  cell_class=self.value_class,
                                  cell_link=self.value_link,
                                  cell_format=self.value_format,
                                  cell_tooltip=self.value_tooltip)
        # Body content
        body_content = list()

        # Column config
        column_config = dict()
        for column in self.data:
            column_config[column] = {
                "class": None,
                "style": None,
                "format": None,
                "tooltip": None,
                "drill": None
            }

            cel_to_column(column, "cell_link", CellGenerator, ColumnGenerator)
            cel_to_column(column, "cell_style", CellGenerator, ColumnGenerator)
            cel_to_column(column, "cell_class", CellGenerator, ColumnGenerator)
            cel_to_column(column, "cell_tooltip", CellGenerator, ColumnGenerator)
            cel_to_column(column, "cell_format", CellGenerator, ColumnGenerator)

            column_config = ColumnGenerator.cell_config(column_config, column)

        # TODO redesign on table json generation
        row_index = 0
        for row_content in table_data:
            #  Row Config
            content = row_content
            content["_lq_row_config"] = self._row_config(row_index, cell_generator=CellGenerator)

            # Cell Config
            content["_lq_cell_config"] = dict()
            for column in self.data:
                if isinstance(self.data[column].iloc[row_index], LooqObject):
                    content["_lq_cell_config"][column] = {
                        "render": {
                            "content": json.loads(
                                self.data[column].iloc[row_index].to_json_structure
                            )
                        }
                    }
                    content[column] = self.data[column].iloc[row_index].value
                    self.data[column].iloc[row_index] = content[column]
                else:
                    content["_lq_cell_config"].update(CellGenerator.cell_config(
                        content["_lq_cell_config"], column, row_index))

            body_content.append(content)
            row_index += 1

        # Create general json
        body_json = {"_lq_column_config": column_config, "content": body_content}

        return body_json

    def _row_config(self, idx, cell_generator=None):
        row_config = {
            "class": self._get_row_class(idx, cell_generator),
            "style": self._get_row_style(idx, cell_generator),
            "format": self._get_row_format(idx, cell_generator),
            "tooltip": self._get_row_tooltip(idx, cell_generator),
            "drill": self._get_row_link(idx, cell_generator)
        }

        return self.remove_json_nones(row_config)

    def _get_row_class(self, idx, cell_generator):
        try:
            row_class_idx = self.row_class.get(idx)
        except TypeError("row_class must be a dict"):
            return None

        # Apply row_class if it is a function
        if isinstance(row_class_idx, types.FunctionType):
            classes = tuple(map(row_class_idx, self.data.iloc[idx]))
            cell_generator.cell_class = {idx: dict(zip(self.data.columns, classes))}

        elif isinstance(row_class_idx, list):
            return row_class_idx

        elif row_class_idx:
            return [row_class_idx]

    def _get_row_format(self, idx, cell_generator):
        try:
            row_format_idx = self.row_format.get(idx)
        except TypeError("row_format must be a dict"):
            return None

        if not isinstance(self.row_format, dict):
            raise TypeError("row_format must be a dict")

        elif isinstance(row_format_idx, types.FunctionType):
            formats = tuple(map(row_format_idx, self.data.iloc[idx]))
            cell_generator.cell_format = {idx: dict(zip(self.data.columns, formats))}

        elif row_format_idx:
            if isinstance(row_format_idx, str):
                return dict(active=True, value=row_format_idx)
            else:
                return dict(active=row_format_idx.get("active", True),
                            value=row_format_idx.get("value"))

    def _get_row_style(self, idx, cell_generator):
        try:
            row_style_idx = self.row_style.get(idx)
        except TypeError("row_style must be a dict"):
            return None

        if isinstance(row_style_idx, types.FunctionType):
            styles = tuple(map(row_style_idx, self.data.iloc[idx]))
            cell_generator.cell_style = {idx: dict(zip(self.data.columns, styles))}

        else:
            return row_style_idx

    def _get_row_tooltip(self, idx, cell_generator):
        try:
            row_tooltip_idx = self.row_tooltip.get(idx)
        except TypeError("row_tooltip must be a dict"):
            return None

        if isinstance(row_tooltip_idx, str):
            return dict(active=True, value=row_tooltip_idx)

        return row_tooltip_idx

    def _get_row_link(self, idx, cell_generator):
        try:
            row_link_idx = self.row_link.get(idx)
        except TypeError("row_link must be a dict"):
            return None

        if any(isinstance(element, list) for element in self.row_link.get(idx, list())):
            links = dict(zip(self.data.columns, zip(*row_link_idx)))
            cell_generator.cell_link.update({idx: links})

        elif isinstance(row_link_idx, str):
            drill_dict = {
                "active": True,
                "mode": "link",
                "content": dict(text=None, link=row_link_idx)
            }
            return drill_dict

        elif row_link_idx:
            drill_dict = {
                "active": True,
                "mode": "dropdown",
                "content": row_link_idx
            }
            return drill_dict
