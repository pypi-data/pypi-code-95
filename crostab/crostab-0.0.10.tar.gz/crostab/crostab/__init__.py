import collections
import json
from dataclasses import dataclass

from veho.columns import column, push_column, pop_column, shift_column, unshift_column
from veho.matrix import init, mapper, shallow, transpose, mutate
from veho.vector import mapper as mapper_vector, mutate as mutate_vector

from crostab.structs import Field
from crostab.enum.keys import HEAD, ROWS, SIDE, TITLE
from crostab.types import Matrix


@dataclass
class Crostab:
    side: list
    head: list
    rows: Matrix
    title: str

    # __slots__ = (SIDE, HEAD, ROWS, TITLE)

    def __init__(self, side, head, rows, title=None, **rest):
        self.side = side
        self.head = head
        self.rows = rows
        self.title = title if title is not None else ''
        if len(rest):
            for key, value in rest.items():
                self.__dict__[key] = value

    @staticmethod
    def ini(side, head, mapper_on_coordinate, title):
        rows = init(len(side), len(head), mapper_on_coordinate)
        return Crostab(side, head, rows, title)

    def to_dict(self):
        return {
            SIDE: self.side,
            HEAD: self.head,
            ROWS: self.rows,
            TITLE: self.title
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def cell(self, r, c):
        return self.rows[x][y] \
            if (x := self.roin(r)) >= 0 and (y := self.coin(c)) >= 0 \
            else None

    def element(self, x, y):
        return self.rows[x][y]

    @property
    def height(self):
        return len(self.side)

    @property
    def width(self):
        return len(self.head)

    def roin(self, field):
        try:
            return self.side.index(field)
        except ValueError:
            return -1

    def coin(self, field):
        try:
            return self.head.index(field)
        except ValueError:
            return -1

    def row(self, side_field):
        return self.rows[x] if (x := self.roin(side_field)) >= 0 else None

    def column(self, head_field):
        return column(self.rows, y) if (y := self.coin(head_field)) >= 0 else None

    def map(self, fn):
        return self.copy(rows=mapper(self.rows, fn))

    def mutate(self, fn):
        return self.boot(rows=mutate(self.rows, fn))

    def map_side(self, fn):
        return self.copy(side=mapper_vector(self.side, fn))

    def mutate_side(self, fn):
        return self.boot(side=mutate_vector(self.side, fn))

    def map_head(self, fn):
        return self.copy(head=mapper_vector(self.head, fn))

    def mutate_head(self, fn):
        return self.boot(head=mutate_vector(self.head, fn))

    def push_row(self, label, row):
        self.side.append(label)
        self.rows.append(row)
        return self

    def pop_row(self):
        side = self.side.pop()
        row = self.rows.pop()
        return Field(side, row)

    def unshift_row(self, label, row):
        self.side.insert(0, label)
        self.rows.insert(0, row)
        return self

    def shift_row(self):
        side = self.side.pop(0)
        row = self.rows.pop(0)
        return Field(side, row)

    def push_column(self, label, column):
        self.head.append(label)
        push_column(self.rows, column)
        return self

    def pop_column(self):
        head = self.head.pop()
        col = pop_column(self.rows)
        return Field(head, col)

    def unshift_column(self, label, column):
        self.head.insert(0, label)
        unshift_column(self.rows, column)
        return self

    def shift_column(self):
        head = self.head.pop(0)
        col = shift_column(self.rows)
        return Field(head, col)

    def set_row(self, side_field, new_row):
        if (x := self.roin(side_field)) < 0: return self
        self.rows[x] = new_row
        return self

    def set_column(self, head_field, new_column):
        if (y := self.coin(head_field)) < 0: return self
        for i, row in enumerate(self.rows): row[y] = new_column[i]
        return self

    def set_row_by(self, side_field, fn):
        if (x := self.roin(side_field)) < 0: return self
        self.rows[x] = [fn(x) for x in self.rows[x]]
        return self

    def set_column_by(self, head_field, fn):
        if (y := self.coin(head_field)) < 0: return self
        for i, row in enumerate(self.rows): row[y] = fn(row[y])
        return self

    def transpose(self, title=None, mutate=True):
        return self.boot(side=self.head, head=self.side, rows=transpose(self.rows), title=title, mutate=mutate)

    def boot(self, side=None, head=None, rows=None, title=None, mutate=True):
        if not mutate: return self.copy(side, head, rows, title)
        if side: self.side = side
        if head: self.head = head
        if rows: self.rows = rows
        if title: self.title = title
        return self

    def copy(self, side=None, head=None, rows=None, title=None):
        if not side: side = self.side[:]
        if not head: head = self.head[:]
        if not rows: rows = shallow(self.rows)
        if not title: title = self.title
        return Crostab(side, head, rows, title)
