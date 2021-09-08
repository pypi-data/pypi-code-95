from texting import CO, COSP, RTSP, SP, join_lines, lange, to_lpad
from veho.vector import mutate

from pyspare.deco.deco_node import mutate_key_pad

lpad = to_lpad(fill=SP, ansi=True)


def render_entries(self, entries, lv):
    vert = 0 if self.vert is None else self.vert
    width = 0 if self.width is None else self.width
    unit = 0 if self.unit is None else self.unit
    rows = mutate(entries, lambda kv: lpad(kv[0], pad) + RTSP + kv[1]) \
        if (lv < vert or any(lange(v) > unit for _, v in entries) or not width) and (pad := mutate_key_pad(entries)) \
        else wrap_entries(entries, width)
    return join_lines(rows, CO, lv) \
        if len(rows) > 1 \
        else COSP.join(rows)


def wrap_entries(entries, width):
    lines = []
    row, wd, kvp, sp = None, 0, None, len(COSP)
    for k, v in entries:
        wd += lange(kvp := k + RTSP + v) + sp
        if row and wd > width:
            lines.append(COSP.join(row))
            row = None
        if not row: row, wd = [], 0
        row.append(kvp)
    if row and len(row): lines.append(COSP.join(row))
    return lines
