from texttab.const import FG_COLOURS, BG_COLOURS

DEFAULT_FG = "white"
DEFAULT_BG = "black"


class Field(object):
    """
    Fields encapsulate advanced features for table cells, like
    custom formatters, colour and the like.

    Colour, in particular, will affect a strings "length" if the terminal
    control sequences are included, as a standard str() method would do.

    To that end, we override the __len__() and __str__() methods.
    """
    def __init__(self, value, fg=None, bg=None, field_name=None, formatters=None):
        self.value = value
        self.name = field_name
        self._fg=fg.lower()
        self._bg=bg.lower()
        self.formatters = formatters

    def __len__(self):
        return len(self.value)

    def __str__(self):
        prefix = FG_COLOURS[self._fg] + BG_COLOURS[self._bg]
        suffix = "\033[0m"
        return prefix + str(self.value) + suffix

    @classmethod
    def from_column(cls, column, value):
        field_fg = DEFAULT_FG
        field_bg = DEFAULT_BG
        if "fg" in column:
            field_fg = column["fg"]
        if "bg" in column:
            field_bg = column["bg"]
        return Field(value, fg=field_fg, bg=field_bg)