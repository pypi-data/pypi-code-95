"""
Basic text-based table classes
"""
import texttab.const as const
from texttab.const import FG_COLOURS, BG_COLOURS


class BasicTable(object):
    def __init__(self, columns=None, border="single", fg=None, bg=None,
                 head_fg=None, head_bg=None):
        self.__col_width_calculated = False

        self.columns = columns
        self.num_columns = len(self.columns)
        self.width = self.calculate_table_width()
        self.generate_column_labels()
        self.rows = []
        self.fg = fg
        self.bg = bg
        self.head_fg = head_fg
        self.head_bg = head_bg

        if border not in const.AVAILABLE_BORDERS:
            exception_string = "Unknown border style: '" + border + "'"
            raise ValueError(exception_string)
        self.border_style = border
        self.border_symbols = const.border_symbols[self.border_style]

    def render(self):
        table_lines = []
        table_lines.append(self._gen_header_top())
        table_lines.append(self.generate_header_line())
        table_lines.append(self._gen_header_bottom())

        for row in self.rows:
            table_lines.append(self._gen_table_row(row))

        table_lines.append(self._gen_table_bottom())

        return table_lines

    def add_row(self, rowdata):
        """
        Provide data to fill in the columns.
        rowdata must be a list or a tuple so that ordering is guaranteed.
        """
        if not isinstance(rowdata, (type(tuple([])), type([]))):
            raise TypeError(
                "Row data can only be expressed as a tuple or list")

        if len(rowdata) < self.num_columns:
            raise ValueError(
                "Insufficient number of data items. "
                "Received {}, expected {}".format(
                    len(rowdata), self.num_columns))
        elif len(rowdata) > self.num_columns:
            raise ValueError(
                "Too many data items. "
                "Received {}, expected {}".format(
                    len(rowdata), self.num_columns))
        self.rows.append(rowdata)

    def calculate_column_widths(self):
        for col in self.columns:
            minimum_width = len(col['label'].strip()) + 2
            if "width" not in col.keys():  # Auto calculate min width
                width = minimum_width
                col['width'] = width
            else:
                if col['width'] < minimum_width:
                    col['width'] = minimum_width

        self.__col_width_calculated = True

    def generate_column_labels(self):
        for col in self.columns:
            generated_label = ""
            if "align" in col.keys():
                if col['align'].lower() in ("center", "centre"):
                    fmt_str = " {:^" + str(col['width'] - 2) + "s} "
                elif col['align'].lower() == "left":
                    fmt_str = " {:" + str(col['width'] - 2) + "s} "
                elif col['align'].lower() == "right":
                    fmt_str = " {:>" + str(col['width'] - 2) + "s} "
            else:
                fmt_str = " {:" + str(col['width'] - 2) + "s} "

            if "head_fg" in col.keys():
                generated_label += const.FG_COLOURS[col["head_fg"]]
            elif "fg" in col.keys():
                generated_label += const.FG_COLOURS[col["fg"]]

            if "head_bg" in col.keys():
                generated_label += const.BG_COLOURS[col["head_bg"]]
            elif "bg" in col.keys():
                generated_label += const.BG_COLOURS[col["bg"]]

            generated_label += fmt_str.format(col['label'])
            generated_label += "\033[0m"
            col['gen_label'] = generated_label

    def calculate_table_width(self):
        if not self.__col_width_calculated:
            self.calculate_column_widths()

        table_width = 0
        for col in self.columns:
            table_width += col['width']

        table_width += 2 + (self.num_columns - 1)
        return table_width

    def get_colour_prefix(self):
        colour_string = ""
        reset_colour = False

        if self.fg is not None:
            colour_string += FG_COLOURS[self.fg]
            reset_colour = True
        if self.bg is not None:
            colour_string += BG_COLOURS[self.bg]
            reset_colour = True

        return colour_string, reset_colour

    def get_head_colour_prefix(self):
        colour_string = ""
        reset_colour = False

        if self.head_fg is not None:
            colour_string += FG_COLOURS[self.head_fg]
            reset_colour = True
        if self.head_bg is not None:
            colour_string += BG_COLOURS[self.head_bg]
            reset_colour = True

        return colour_string, reset_colour


    def generate_header_line(self):
        line = ""
        colour_string, reset_colours = self.get_head_colour_prefix()

        line += colour_string + self.border_symbols['VBAR']
        column_labels = [col['gen_label'] for col in self.columns]
        line += (colour_string + self.border_symbols["VBAR"]).join(column_labels)
        line += colour_string + self.border_symbols["VBAR"]

        if reset_colours is True:
            line += "\033[0m"
        return line

    def _gen_header_top(self):
        line = ""
        reset_colours = False

        if self.head_fg is not None:
            line += FG_COLOURS[self.head_fg]
            reset_colours = True
        if self.head_bg is not None:
            line += BG_COLOURS[self.head_bg]
            reset_colours = True

        line += self.border_symbols["TOP_LEFT"]
        col_bars = [
            col['width'] * self.border_symbols["HBAR"] for col in self.columns
        ]
        line += self.border_symbols["TOP_TEE"].join(col_bars)
        line += self.border_symbols["TOP_RIGHT"]

        if reset_colours is True:
            line += "\033[0m"
        return line

    def _gen_header_bottom(self):
        line = ""
        colour_string, reset_colours = self.get_head_colour_prefix()

        line += colour_string  # Begin our colour, column value might overwrite
        line += self.border_symbols["LEFT_TEE"]
        col_bars = [
            col['width'] * self.border_symbols["HBAR"] for col in self.columns
        ]
        line += colour_string + self.border_symbols["INTERSECT"].join(col_bars)
        line += colour_string + self.border_symbols["RIGHT_TEE"]

        if reset_colours is True:
            line += "\033[0m"

        return line

    def _gen_table_bottom(self):
        colour_string, reset_colours = self.get_colour_prefix()

        line = colour_string + self.border_symbols["BOTTOM_LEFT"]
        col_bars = [
            col['width'] * self.border_symbols["HBAR"] for col in self.columns
        ]
        line += (colour_string + self.border_symbols["BOTTOM_TEE"]).join(col_bars)
        line += colour_string + self.border_symbols["BOTTOM_RIGHT"]

        if reset_colours is True:
            line = line + "\033[0m"
        return line

    def _gen_table_row(self, rowdata):
        colour_string, reset_colours = self.get_colour_prefix()

        line = colour_string + self.border_symbols["VBAR"]
        col_strings = []

        for col_index, col in enumerate(self.columns):
            fmt_str = self._get_column_format_string(col)
            col_string = self.format_column_value(
                col, rowdata[col_index], fmt_str)
            col_strings.append(col_string)
        line += (colour_string + self.border_symbols["VBAR"]).join(col_strings)
        line += colour_string + self.border_symbols["VBAR"]

        if reset_colours is True:
            line += "\033[0m"

        return line

    def format_column_value(self, col, rowdata, fmtstr):
        # cell_field = Field.from_column(col, rowdata)
        ret_str = ""
        colour_string = ""
        reset_colour = False

        # Prefix our colour options, as ANSI codes
        if "fg" in col.keys():
            colour_string += FG_COLOURS[col["fg"]]
            reset_colour = True
        if "bg" in col.keys():
            colour_string += BG_COLOURS[col["bg"]]
            reset_colour = True
        if "bold" in col.keys():
            colour_string += "\033[1m"
            reset_colour = True
        if "invert" in col.keys():
            colour_string += "\033[7m"
            reset_colour = True

        # Get our width-padded value string, no colour modifiers to affect
        # length calculations.
        if 'formatter' in col.keys():
            colour_string, value_str, reset_colour = col['formatter'].format(rowdata, col)
        else:
            value_str = str(rowdata)
            # value_str = str(cell_field)
            if len(value_str) > col['width'] - 2:
                value_str = value_str[:col['width'] - 5] + "..."
        ret_str += colour_string + fmtstr.format(value_str)

        # Reset ANSI sequence if we tweaked any colour options
        if reset_colour is True:
            ret_str += "\033[0m"

        return ret_str

    def _get_column_format_string(self, col):
        if "align" not in col.keys() or col["align"] == "left":
            fmt_str = "{:" + str(col['width']) + "}"
        elif col["align"] == "right":
            fmt_str = "{:>" + str(col['width']) + "}"
        elif col["align"] in ("center", "centre"):
            fmt_str = "{:^" + str(col['width']) + "}"
        return fmt_str
