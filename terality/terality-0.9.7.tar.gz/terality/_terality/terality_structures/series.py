import pandas as pd

from . import ClassMethod, Struct
from .structure import StructIterator


class ClassMethodSeries(ClassMethod):
    _class_name: str = "series"
    _pandas_class = pd.Series
    _additional_class_methods = ClassMethod._additional_class_methods | {
        "random",
        "random_integers",
    }


class Series(Struct, metaclass=ClassMethodSeries):
    _pandas_class_instance = pd.Series(dtype="float64")
    _accessors = {"str", "dt"}
    _additional_methods = Struct._additional_methods | {"get_range_auto", "random"}

    def __iter__(self):
        return StructIterator(self)

    def to_dict(self):
        pd_series = self._call_method(None, "to_dict")
        return pd_series.to_dict()

    def to_list(self):
        pd_series = self._call_method(None, "to_list")
        return pd_series.to_list()

    def tolist(self):
        return self.to_list()
