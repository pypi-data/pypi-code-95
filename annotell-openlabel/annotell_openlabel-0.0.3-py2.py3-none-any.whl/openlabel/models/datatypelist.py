from dataclasses import dataclass
from typing import Generic, List, MutableSequence, TypeVar

from annotell.openlabel.models.data_types import Boolean, DataTypeBase, Num, Text, Vec

T = TypeVar("T", Boolean, Num, Text, Vec)


@dataclass
class DataTypeList(MutableSequence, Generic[T]):
    """
    List-like object containing basetypes for openlabel.
    Ensures no duplicate values when merging several OpenLABEL objects.
    Needed to avoid conflicting values after merging, for example that something
    is both "visible": True and "visible": False
    """

    def __init__(self, *args):
        self.list: List[DataTypeBase] = list()

        if args is None or args == ():
            return

        self.extend(*args)

    def __contains__(self, item: DataTypeBase):
        return any([el.name == item.name for el in self.list])

    def __add__(self, other):
        new_dtc = DataTypeList([])
        new_dtc.extend(self)
        new_dtc.extend(other)
        return new_dtc

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __delitem__(self, i):
        del self.list[i]

    def __setitem__(self, i, item):
        if self._check(item):
            self.list[i] = item

    def __repr__(self):
        return f"DataTypeList({self.list.__repr__()})"

    def __str__(self):
        return f"DataTypeList({self.list.__str__()})"

    def _check(self, item: DataTypeBase) -> bool:
        assert isinstance(item, DataTypeBase), "Only DataTypeBase supported for DataTypeCollection"

        if item in self:
            self_item = [i for i in self.list if i.name == item.name][0]
            if self_item.val != item.val:
                raise AttributeError("Can add DataType with same name and different value to DataTypeCollection")
            return False
        return True

    def append(self, item: DataTypeBase):
        if self._check(item):
            self.list.append(item)

    def insert(self, index: int, item: DataTypeBase):
        if self._check(item):
            self.list.insert(index, item)

    def extend(self, items):
        for item in items:
            self.append(item)

    def merge_with(self, other):
        return self.__add__(other)
