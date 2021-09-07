import typing



# +--- border-top -----------------------------------------------+-----------------+
# | main                                                         |                 |
# |                                                              |                 |
# |                                                              |                 |
# |                                                              |                 |
# |                                                              |                 |
# |--- border bottom --------------------------------------------+-----------------|


class Text(typing.NamedTuple):
    attr: int
    fg: int
    bg: int
    text: str
    reset: bool


class Buffer(typing.NamedTuple):
    lines: typing.List[Text]



class Hang(typing.NamedTuple):
    buffer: Buffer


class Split(typing.NamedTuple):
    """
    Horizontal or verticle split of the terminal screen.
    """
    is_horizontal: bool
    hang_right: Hang
    hang_left: Hang
    buffer: Buffer


class Layer(typing.NamedTuple):
    splits: typing.List[Split]
    depth: int
    is_active: bool
