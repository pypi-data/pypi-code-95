from typing import Any, Callable, Dict, List

import pandas as pd

from terality_serde import loads
from common_client_scheduler import (
    Display,
    ExportResponse,
    StructRef,
    IndexColNames,
    PandasIndexMetadata,
    PandasSeriesMetadata,
    PandasDFMetadata,
    NDArrayMetadata,
)

from .. import DataTransfer, copy_to_user_s3_bucket
from ..awscredshelper import AwsCredentialsFetcher
from ..utils.azure import test_for_azure_libs, parse_azure_filesystem
from .. import global_client


def _deserialize_display(
    aws_credentials: AwsCredentialsFetcher, to_display: Display
):  # pylint: disable=unused-argument,useless-return
    # No need to force it in package dependencies, if it gets called it means we are in a Jupyter Notebook
    # and and this dependency is present
    # noinspection PyUnresolvedReferences
    from IPython.display import display, HTML

    display(HTML(to_display.value))


def _deserialize_export(aws_credentials: AwsCredentialsFetcher, export: ExportResponse) -> None:
    path = export.path
    transfer_id = export.transfer_id
    if path.startswith("s3://"):
        copy_to_user_s3_bucket(
            aws_credentials.get_credentials(), transfer_id, export.aws_region, path
        )
    elif path.startswith("abfs://") or path.startswith("az://"):
        test_for_azure_libs()
        from ..data_transfers.azure import copy_to_azure_datalake

        storage_account_name, container, path = parse_azure_filesystem(path, export.storage_options)
        copy_to_azure_datalake(
            aws_credentials=aws_credentials.get_credentials(),
            transfer_id=transfer_id,
            aws_region=export.aws_region,
            storage_account_name=storage_account_name,
            container=container,
            path_template=path,
        )
    else:
        DataTransfer.download_to_local_files(
            global_client().get_download_config(),
            aws_credentials.get_credentials(),
            transfer_id,
            path,
            export.is_folder,
        )


def _download_ndarray_from_metadata(
    aws_credentials: AwsCredentialsFetcher, ndarray_metadata: NDArrayMetadata
):
    # noinspection PyTypeChecker
    # TODO use np.load, but we have to upload accordingly within scheduler ndarray_to_numpy_metadata.
    df = _download_df(
        aws_credentials, ndarray_metadata.transfer_id, ndarray_metadata.cols_json_encoded
    )
    assert len(df.columns) == 1
    return df.iloc[:, 0].to_numpy()


def _download_df(
    aws_credentials: AwsCredentialsFetcher, transfer_id: str, is_col_json: List[bool]
) -> pd.DataFrame:
    df: pd.DataFrame = pd.read_parquet(
        DataTransfer.download_to_bytes(
            global_client().get_download_config(), aws_credentials.get_credentials(), transfer_id  # type: ignore
        )
    )
    # Some data types require post-processing.
    for col_num in range(len(is_col_json)):  # pylint: disable=consider-using-enumerate
        if is_col_json[col_num]:
            df.iloc[:, col_num] = df.iloc[:, col_num].apply(loads)
    return df


def _rename_index(index: pd.Index, index_col_names: IndexColNames):
    if isinstance(index, pd.MultiIndex):
        index.names = index_col_names.names
    index.name = index_col_names.name


def _download_index_from_metadata(
    aws_credentials: AwsCredentialsFetcher, index_metadata: PandasIndexMetadata
) -> pd.Index:
    df = _download_df(aws_credentials, index_metadata.transfer_id, index_metadata.cols_json_encoded)
    if len(df.columns) == 1:
        index = pd.Index(data=df.iloc[:, 0])
    else:
        index = pd.MultiIndex.from_arrays([df.iloc[:, i] for i in range(len(df.columns))])
    _rename_index(index, index_metadata.index_col_names)
    return index


def _download_series_from_metadata(
    aws_credentials: AwsCredentialsFetcher, series_metadata: PandasSeriesMetadata
) -> pd.Series:
    df = _download_df(
        aws_credentials, series_metadata.transfer_id, series_metadata.cols_json_encoded
    )
    series = df.iloc[:, 0]
    series.name = series_metadata.series_name
    _rename_index(series.index, series_metadata.index_col_names)
    return series


def _download_df_from_metadata(
    aws_credentials: AwsCredentialsFetcher, df_metadata: PandasDFMetadata
) -> pd.DataFrame:
    df = _download_df(aws_credentials, df_metadata.transfer_id, df_metadata.cols_json_encoded)
    df.columns = df_metadata.col_names
    df.columns.name = df_metadata.col_names_name  # type: ignore
    _rename_index(df.index, df_metadata.index_col_names)
    return df


_decoder: Dict[Any, Callable[[AwsCredentialsFetcher, Any], Any]] = {
    NDArrayMetadata: _download_ndarray_from_metadata,
    PandasIndexMetadata: _download_index_from_metadata,
    PandasSeriesMetadata: _download_series_from_metadata,
    PandasDFMetadata: _download_df_from_metadata,
    Display: _deserialize_display,
    ExportResponse: _deserialize_export,
}


def decode(credentials_fetcher: AwsCredentialsFetcher, o):  # pylint: disable=invalid-name
    from terality import (
        NDArray,
        Index,
        MultiIndex,
        Series,
        DataFrame,
    )  # To avoid circular dependencies
    from terality._terality.terality_structures import DataFrameGroupBy, SeriesGroupBy

    structs = {
        "ndarray": NDArray,
        "index": Index,
        "multi_index": MultiIndex,
        "series": Series,
        "dataframe": DataFrame,
        "groupby_df": DataFrameGroupBy,
        "groupby_series": SeriesGroupBy,
    }

    if isinstance(o, StructRef):
        # noinspection PyProtectedMember
        return structs[o.type]._new(id_=o.id)
    if type(o) in _decoder:
        return _decoder[type(o)](credentials_fetcher, o)
    return o
