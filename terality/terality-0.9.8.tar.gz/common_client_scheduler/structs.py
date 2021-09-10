from dataclasses import dataclass
from typing import Hashable, List, Optional

from terality_serde import SerdeMixin


@dataclass
class StructRef(SerdeMixin):
    type: str  # 'index' 'series' 'multi_index' 'df_groupby'
    id: str  # pylint: disable=invalid-name


@dataclass
class IndexColNames(SerdeMixin):
    names: List[Hashable]
    name: Hashable


@dataclass
class InMemoryObjectMetadata(SerdeMixin):
    """
    When to_pandas/from_pandas methods are performed, these metadata
    are sent between client/scheduler instead of raw data.
    """

    transfer_id: str
    cols_json_encoded: List[bool]


@dataclass
class NDArrayMetadata(InMemoryObjectMetadata, SerdeMixin):
    pass


@dataclass
class PandasIndexMetadata(InMemoryObjectMetadata, SerdeMixin):
    index_col_names: IndexColNames


@dataclass
class PandasSeriesMetadata(InMemoryObjectMetadata, SerdeMixin):
    index_col_names: IndexColNames
    series_name: Hashable


@dataclass
class PandasDFMetadata(InMemoryObjectMetadata, SerdeMixin):
    index_col_names: IndexColNames
    col_names: List[Hashable]
    col_names_name: Hashable


@dataclass
class Display(SerdeMixin):
    value: str


@dataclass
class PandasFunctionRequest(SerdeMixin):
    function_type: str
    function_accessor: Optional[str]
    function_name: str
    args: str
    kwargs: str
