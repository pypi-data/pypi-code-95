from io import BytesIO
from typing import Any, Callable, List, Optional, Tuple

import numpy as np
import pandas as pd
import pyarrow.lib
import terality
from terality.exceptions import TeralityClientError

from terality_serde import CallableWrapper, dumps
from common_client_scheduler import (
    StructRef,
    IndexColNames,
    PandasIndexMetadata,
    PandasSeriesMetadata,
    PandasDFMetadata,
    NDArrayMetadata,
)
from .. import DataTransfer, global_client
from ..awscredshelper import AwsCredentialsFetcher


def _check_if_col_needs_json_encoding(col: pd.Series) -> bool:
    if isinstance(col.dtype, np.dtype) and col.dtype.hasobject:
        # Collect the types of all values in the column.
        dtypes = set()
        for value in col:
            dtypes.add(type(value))
        # Ignore absent values: they are gracefully handled by the Parquet format.
        dtypes -= {type(None)}

        # Based on the combination of types, decide if we need to JSON-encode.
        need_json = len(dtypes) > 1 or any(dtype in dtypes for dtype in [list, dict])
        return need_json
    return False


def _prepare_for_parquet(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[bool]]:
    is_col_json = []
    for col_num in range(len(df.columns)):
        col_needs_json = _check_if_col_needs_json_encoding(df.iloc[:, col_num])
        if col_needs_json:
            df.iloc[:, col_num] = df.iloc[:, col_num].apply(dumps)
        is_col_json.append(col_needs_json)
    return df, is_col_json


def _upload_df(aws_credentials: AwsCredentialsFetcher, df: pd.DataFrame) -> Tuple[str, List[bool]]:
    """Parquet only supports dataframes so we transmit all pandas structures as dataframes"""
    # WARNING: Parquet only accepts string column names
    # => We replace non-string column names with placeholders and pass the columns "out of band" (in the metadata).
    df = df.rename(
        columns={df.columns[col_num]: str(col_num) for col_num in range(len(df.columns))},
        copy=False,
    )

    df, is_col_json = _prepare_for_parquet(df)
    row_group_size = _estimate_row_group_size(df, 1024 ** 3)

    data_bytes = BytesIO()
    df.to_parquet(data_bytes, version="2.0", row_group_size=row_group_size)
    import_id = DataTransfer.upload_bytes(
        global_client().get_upload_config(), aws_credentials.get_credentials(), data_bytes  # type: ignore
    )
    return import_id, is_col_json


def _estimate_row_group_size(df: pd.DataFrame, max_memory_per_row_group_bytes=1024 ** 3) -> int:
    """Estimate the size of a parquet row group that can be processed in memory for this dataframe,
    index included.

    In other words, split the dataframe in row groups, each row group not exceeding
    `max_memory_per_row_group_bytes`, and return the size (in rows) of a row group.

    Server-side, we can only process parquet files by row group. We can not split a parquet file in the
    middle of a row group. This means that a whole uncompressed row group must fit in memory. In order to
    maximize parallelisation server-side, this function returns how many rows per row group the parquet file
    should contain.

    We still want this value to be as high as possible to improve compression and reduce the bandwidth
    used, but err on the side of caution - an incorrect split means we can't easily process the uploaded
    files (we risk returning memory errors, which would be unfortunate for Terality :) ).

    We also want this operation to be as fast as possible, so we don't use `memory_usage(deep=True)`, which
    is costly on big datasets. Instead, for columns with dtype = object, we take a guess based on a small
    sample and hope it covers all real-world usage. This function may fail on dataframes that have a wide
    distribution of object sizes.
    """
    # as a safety measure, never include more than this many rows per row group.
    # this should give us a safety net even if our memory usage estimation is wildly inaccurate.
    MAX_ROWS_PER_ROW_GROUP = 2_000_000  # pylint: disable=invalid-name

    memory_usage_bytes = _estimate_dataframe_memory_usage_bytes(df)
    rows_per_row_group = (len(df) * max_memory_per_row_group_bytes) // memory_usage_bytes

    return min(rows_per_row_group, MAX_ROWS_PER_ROW_GROUP)


def _estimate_dataframe_memory_usage_bytes(
    df: pd.DataFrame, max_samples: int = 500, random_state=None
) -> int:
    """Estimate the memory usage of a DataFrame, in bytes.

    See _estimate_column_memory_usage_bytes for the difference with `memory_usage(deep=True)`.
    """
    # Get memory usage for all columns, except when dtype = object.
    memory_usage = df.memory_usage(deep=False)
    total_memory_bytes = 0

    object_columns = [column for column, dtype in df.dtypes.iteritems() if dtype == "object"]
    nonobject_columns = [column for column, dtype in df.dtypes.iteritems() if dtype != "object"]

    for nonobject_column in nonobject_columns:
        total_memory_bytes += memory_usage[nonobject_column]

    estimate_index_memory_use = True
    # Index could be a MultiIndex too, without a single dtype. For those, we'll also rely on sampling.
    if isinstance(df.index, pd.Index) and df.index.dtype != "object":
        # Use exact memory usage for single-level indexes with a non-object dtype.
        total_memory_bytes += memory_usage["Index"]
        estimate_index_memory_use = False

    total_memory_bytes += _estimate_columns_memory_usage_bytes(
        df, object_columns, estimate_index_memory_use, max_samples, random_state
    )

    return total_memory_bytes


def _estimate_columns_memory_usage_bytes(
    df: pd.DataFrame,
    columns: List[str],
    include_index: bool,
    max_samples: int = 200,
    random_state=None,
) -> int:
    """Estimate the memory usage of columns in a DataFrame, in bytes.

    Unlike memory_usage(deep=True), this function samples rows and extrapolate the memory usage from these
    rows only. This makes it faster, but inaccurate.

    If `columns` is an empty list, the memory usage of the index will still be included in the return when
    include_index is True.

    The sample is random, and thus the results of this function are not reproducible unless random_state is
    provided.
    """
    df_columns: pd.DataFrame = df[columns]
    samples_count: int = min(max_samples, len(df_columns))
    samples: pd.DataFrame = df_columns.sample(n=samples_count, random_state=random_state)
    return (
        samples.memory_usage(deep=True, index=include_index).sum().squeeze()
        / samples_count
        * len(df_columns)
    )


def _make_index_col_names(index: pd.Index) -> IndexColNames:
    return IndexColNames(names=list(index.names), name=index.name)


# def _serialize_ndarray(aws_credentials: AwsCredentialsFetcher, array: np.ndarray) -> str:
#     data_bytes = BytesIO()
#     # noinspection PyTypeChecker
#     np.save(data_bytes, array)
#     import_id = DataTransfer.upload_bytes(
#         global_client().get_upload_config(), aws_credentials.get_credentials(), data_bytes  # type: ignore
#     )
#     return import_id


# TODO the above version is more opti to upload/store data,
#  check how to read with numpy scheduler side (ndarray_from_numpy_metadata)
def _upload_ndarray_and_get_metadata(
    aws_credentials: AwsCredentialsFetcher, ndarray: np.ndarray
) -> NDArrayMetadata:
    transfer_id, is_col_json = _upload_df(aws_credentials, pd.DataFrame(ndarray))
    return NDArrayMetadata(
        transfer_id=transfer_id,
        cols_json_encoded=is_col_json,
    )


def _upload_index_and_get_metadata(
    aws_credentials: AwsCredentialsFetcher, index: pd.Index
) -> PandasIndexMetadata:
    transfer_id, is_col_json = _upload_df(aws_credentials, index.to_frame(index=False))
    return PandasIndexMetadata(
        transfer_id=transfer_id,
        cols_json_encoded=is_col_json,
        index_col_names=_make_index_col_names(index),
    )


def _upload_series_and_get_metadata(
    aws_credentials: AwsCredentialsFetcher, series: pd.Series
) -> PandasSeriesMetadata:
    transfer_id, is_col_json = _upload_df(aws_credentials, series.copy(deep=True).to_frame())
    return PandasSeriesMetadata(
        transfer_id=transfer_id,
        cols_json_encoded=is_col_json,
        index_col_names=_make_index_col_names(series.index),
        series_name=series.name,
    )


def _upload_df_and_get_metadata(
    aws_credentials: AwsCredentialsFetcher, df: pd.DataFrame
) -> PandasDFMetadata:
    transfer_id, is_col_json = _upload_df(aws_credentials, df.copy(deep=True))
    return PandasDFMetadata(
        transfer_id=transfer_id,
        cols_json_encoded=is_col_json,
        index_col_names=_make_index_col_names(df.index),
        col_names=list(df.columns),
        col_names_name=df.columns.name,
    )


def _to_terality(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return terality.NDArray.from_numpy(obj)
    if isinstance(obj, pd.Index):
        return terality.Index.from_pandas(obj)
    if isinstance(obj, pd.Series):
        return terality.Series.from_pandas(obj)
    if isinstance(obj, pd.DataFrame):
        return terality.DataFrame.from_pandas(obj)
    return obj


def _get_upload_method(obj: Any) -> Optional[Callable[[AwsCredentialsFetcher, Any], Any]]:
    if isinstance(obj, np.ndarray):
        if len(obj.shape) != 1:
            raise TeralityClientError("Terality only supports 1D numpy array.")
        return _upload_ndarray_and_get_metadata
    if isinstance(obj, pd.Index):
        return _upload_index_and_get_metadata
    if isinstance(obj, pd.Series):
        return _upload_series_and_get_metadata
    if isinstance(obj, pd.DataFrame):
        return _upload_df_and_get_metadata
    return None


def _upload_object_and_get_metadata(
    credentials_fetcher: AwsCredentialsFetcher, upload_method: Callable, obj: Any
):
    """
    When XXX.from_pandas is called, we upload pandas object data in S3 and we send metadata to the scheduler.
    The scheduler will then deserialize the metadata, then build and return a Terality structure to the client.
    """

    try:
        return upload_method(credentials_fetcher, obj)
    except pyarrow.lib.ArrowNotImplementedError as e:
        message = str(e)
        # Simplify the user facing error message
        message = message.replace("Unhandled type for Arrow to Parquet schema conversion: ", "")
        raise TeralityClientError(
            f"Terality can not transfer the data structure: unsupported data type: {message}"
        ) from e


def encode(credentials_fetcher: AwsCredentialsFetcher, function_name: str, obj: Any):
    from terality import NDArray, Index, Series, DataFrame  # Avoid circular dependencies
    from terality._terality.terality_structures import DataFrameGroupBy, SeriesGroupBy

    if function_name in ["from_pandas", "from_numpy"]:
        upload_method = _get_upload_method(obj)
        if upload_method is not None:
            return _upload_object_and_get_metadata(credentials_fetcher, upload_method, obj)
        raise ValueError(f"Can't convert type {type(obj)} to terality structure")
    try:
        obj = _to_terality(obj)
    except Exception as e:
        raise ValueError(
            f"An error occured while converting parameter {obj} into a Terality structure"
        ) from e

    if isinstance(obj, (NDArray, Index, Series, DataFrame, DataFrameGroupBy, SeriesGroupBy)):
        # noinspection PyProtectedMember
        return StructRef(id=obj._id, type=obj.__class__._class_name)
    if callable(obj) and not isinstance(obj, type):  # avoid types, which are also callables
        return CallableWrapper.from_object(obj)

    return obj
