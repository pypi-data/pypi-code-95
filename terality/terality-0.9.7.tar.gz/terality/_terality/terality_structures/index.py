from typing import Set

import pandas as pd

from . import ClassMethod, Struct, StructIterator


class ClassMethodIndex(ClassMethod):
    _class_name: str = "index"
    _pandas_class = pd.Index


class Index(Struct, metaclass=ClassMethodIndex):
    _pandas_class_instance = pd.Index([])
    _accessors = {"str"}
    _additional_methods = Struct._additional_methods | {"get_range_auto"}
    _indexers: Set[str] = set()

    def __iter__(self):
        return StructIterator(self)


class ClassMethodMultiIndex(ClassMethodIndex):
    _class_name: str = "multi_index"
    _pandas_class = pd.MultiIndex


class MultiIndex(Index, metaclass=ClassMethodMultiIndex):
    _pandas_class_instance = pd.MultiIndex(levels=[[0, 1], [2, 3]], codes=[[0, 1], [0, 1]])
