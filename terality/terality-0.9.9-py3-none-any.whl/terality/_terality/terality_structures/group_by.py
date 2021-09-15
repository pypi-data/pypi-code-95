from pandas.core import groupby
from terality_serde import StructType

from . import ClassMethod, Struct


class ClassMethodGroupBySeries(ClassMethod):
    _class_name: str = StructType.SERIES_GROUPBY
    # noinspection PyUnresolvedReferences
    _pandas_class = groupby.SeriesGroupBy


class SeriesGroupBy(Struct, metaclass=ClassMethodGroupBySeries):
    # noinspection PyUnresolvedReferences
    _pandas_class_instance = groupby.SeriesGroupBy
    _additional_methods = Struct._additional_methods | {"sum", "mean"}


class ClassMethodGroupByDF(ClassMethod):
    _class_name: str = StructType.DATAFRAME_GROUPBY
    # noinspection PyUnresolvedReferences
    _pandas_class = groupby.DataFrameGroupBy


class DataFrameGroupBy(Struct, metaclass=ClassMethodGroupByDF):
    # noinspection PyUnresolvedReferences
    _pandas_class_instance = groupby.DataFrameGroupBy
    _additional_methods = Struct._additional_methods | {"sum", "mean"}

    def _on_missing_attribute(self, item: str):
        return self._call_method(None, "df_groupby_attribute_access", item)
