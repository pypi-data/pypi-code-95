from dataclasses import dataclass

from veho.columns import column
from veho.matrix import size, mapper, shallow, transpose, mutate
from veho.vector import mapper as mapper_vector, mutate as mutate_vector

from crostab.types import Matrix


@dataclass
class Table:
    head: list
    rows: Matrix
    title: str

    # __slots__ = (HEAD, ROWS, TITLE, TYPES)

    def __init__(self, head: list, rows: list, title: str = None, **rest):
        self.title = title if title is not None else ''
        self.rows = rows
        self.head = head
        if len(rest):
            for key, value in rest.items():
                self.__setattr__(key, value)

    @staticmethod
    def from_json(json_ob, title):
        j = json_ob.loads(json_ob)
        return Table(j.head, j.rows, title)

    @staticmethod
    def from_dict(dict_ob):
        return Table(**dict_ob)  # head, rows, title, types

    @property
    def size(self):
        return size(self.rows)

    @property
    def height(self):
        return len(self.rows)

    @property
    def width(self):
        return len(self.head)

    @property
    def columns(self):
        return transpose(self.rows)

    def cell(self, x, y):
        return self.rows[x][y]

    def coin(self, field):
        try:
            return field if isinstance(field, int) else self.head.index(field)
        except ValueError:
            return -1

    def column_indexes(self, fields):
        return [self.coin(field) for field in fields]

    def column(self, field):
        return column(self.rows, y) if (y := self.coin(field)) >= 0 else None

    def map(self, fn):
        return self.copy(rows=mapper(self.rows, fn))

    def mutate(self, fn):
        return self.boot(rows=mutate(self.rows, fn))

    def map_head(self, fn):
        return self.copy(head=mapper_vector(self.head, fn))

    def mutate_head(self, fn):
        return self.boot(head=mutate_vector(self.head, fn))

    def set_column(self, field, new_column):
        if (y := self.coin(field)) < 0: return self
        for i, row in enumerate(self.rows): row[y] = new_column[i]
        return self

    def set_column_by(self, field, mapper):
        if (y := self.coin(field)) < 0: return self
        for i, row in enumerate(self.rows): row[y] = mapper(row[i])
        return self

    def boot(self, head=None, rows=None, title=None, mutate=True):
        if not mutate: return self.copy(head, rows, title)
        if head: self.head = head
        if rows: self.rows = rows
        if title: self.title = title
        return self

    def copy(self, head=None, rows=None, title=None):
        if not head: head = self.head[:]
        if not rows: rows = shallow(self.rows)
        if not title: title = self.title
        return Table(head, rows, title)
