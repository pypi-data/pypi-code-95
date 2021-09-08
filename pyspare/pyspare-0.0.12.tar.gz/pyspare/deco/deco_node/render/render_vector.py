from texting import CO, COSP, lange

from texting import join_lines


def render_vector(self, vector, lv):
    vert = 0 if self.vert is None else self.vert
    width = 0 if self.width is None else self.width
    unit = 0 if self.unit is None else self.unit
    rows = vector \
        if lv < vert or any(lange(x) > unit for x in vector) or not width \
        else wrap_vector(vector, width)
    return join_lines(rows, CO, lv) \
        if len(rows) > 1 \
        else COSP.join(vector)


def wrap_vector(vector, width):
    lines = []
    row, size, sp = None, 0, len(COSP)
    for item in vector:
        size += lange(item) + sp
        if row and size > width:
            lines.append(COSP.join(row))
            row = None
        if not row: row, size = [], 0
        row.append(item)
    return lines
