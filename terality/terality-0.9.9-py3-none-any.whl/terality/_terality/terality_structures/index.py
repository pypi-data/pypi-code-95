from typing import Set

import pandas as pd
from terality_serde import IndexType

from . import ClassMethod, Struct, StructIterator


class ClassMethodIndex(ClassMethod):
    _class_name: str = IndexType.INDEX
    _pandas_class = pd.Index


class Index(Struct, metaclass=ClassMethodIndex):
    _pandas_class_instance = pd.Index([])
    _accessors = {"str"}
    _additional_methods = Struct._additional_methods | {"get_range_auto"}
    _indexers: Set[str] = set()

    def __iter__(self):
        return StructIterator(self)


class ClassMethodMultiIndex(ClassMethodIndex):
    _class_name: str = IndexType.MULTI_INDEX
    _pandas_class = pd.MultiIndex


class MultiIndex(Index, metaclass=ClassMethodMultiIndex):
    _pandas_class_instance = pd.MultiIndex(levels=[[0, 1], [2, 3]], codes=[[0, 1], [0, 1]])


class ClassMethodDatetimeIndex(ClassMethodIndex):
    _class_name: str = IndexType.DATETIME_INDEX
    _pandas_class = pd.DatetimeIndex


class DatetimeIndex(Index, metaclass=ClassMethodDatetimeIndex):
    _pandas_class_instance = pd.DatetimeIndex([])


class ClassMethodInt64Index(ClassMethodIndex):
    _class_name: str = IndexType.INT64_INDEX
    _pandas_class = pd.Int64Index


class Int64Index(Index, metaclass=ClassMethodInt64Index):
    _pandas_class_instance = pd.Int64Index([])


class ClassMethodFloat64Index(ClassMethodIndex):
    _class_name: str = IndexType.FLOAT64_INDEX
    _pandas_class = pd.Float64Index


class Float64Index(Index, metaclass=ClassMethodFloat64Index):
    _pandas_class_instance = pd.Float64Index([])
