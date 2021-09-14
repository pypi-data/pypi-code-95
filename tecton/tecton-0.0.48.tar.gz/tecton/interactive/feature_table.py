from datetime import datetime
from io import BytesIO
from typing import Mapping
from typing import Optional
from typing import Union

import numpy as np
import pandas
import pendulum
import pyspark
import requests
from pyspark.sql.types import StructType

from tecton import conf
from tecton._internals import errors
from tecton._internals import metadata_service
from tecton._internals.sdk_decorators import sdk_public_method
from tecton.feature_services.query_helper import _QueryHelper
from tecton.interactive.data_frame import DataFrame
from tecton.interactive.data_frame import FeatureVector
from tecton.interactive.feature_definition import FeatureDefinition
from tecton.tecton_context import TectonContext
from tecton_proto.data import feature_view_pb2
from tecton_proto.metadataservice.metadata_service_pb2 import GetFeatureViewRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetNewIngestDataframeInfoRequest
from tecton_proto.metadataservice.metadata_service_pb2 import IngestDataframeRequest
from tecton_spark.logger import get_logger
from tecton_spark.schema import Schema

logger = get_logger("FeatureTable")

__all__ = ["FeatureTable", "get_feature_table"]


class FeatureTable(FeatureDefinition):
    """
    FeatureTable class.

    To get a FeatureTable instance, call :py:func:`tecton.get_feature_table`.
    """

    _proto: feature_view_pb2.FeatureView

    def __init__(self, proto):
        self._proto = proto

    @classmethod
    def _fco_type_name_singular_snake_case(cls) -> str:
        return "feature_table"

    @classmethod
    def _fco_type_name_plural_snake_case(cls) -> str:
        return "feature_tables"

    def __str__(self):
        return f"FeatureTable|{self.id}"

    def __repr__(self):
        return f"FeatureTable(name='{self.name}')"

    @property  # type: ignore
    @sdk_public_method
    def type(self):
        """
        Returns the FeatureTable type.
        """
        return "FeatureTable"

    def timestamp_key(self) -> str:
        """
        Returns the timestamp_key column name of this FeatureTable.
        """
        return self._proto.timestamp_key

    @sdk_public_method
    def get_features(
        self,
        entities: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, None] = None,
        start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
    ) -> DataFrame:
        """
        Gets all features that are defined by this FeatureTable.

        :param entities: (Optional) A DataFrame that is used to filter down feature values.
            If specified, this DataFrame should only contain join key columns.
        :param start_time: (Optional) The interval start time from when we want to retrieve features.
        :param end_time:  (Optional) The interval end time until when we want to retrieve features.

        :return: A Tecton DataFrame with features values.
        """

        return self.get_historical_features(start_time=start_time, end_time=end_time, entities=entities)

    @sdk_public_method
    def get_historical_features(
        self,
        spine: Optional[Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame]] = None,
        timestamp_key: str = None,
        entities: Optional[Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame]] = None,
        start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        save_dataset: bool = False,
        save_as: Optional[str] = None,
    ) -> DataFrame:
        """
        Returns a Tecton :class:`DataFrame` of historical values for this feature table.
        Either provide a spine to join against or set parameters start_time, end_time, and/or entities to specify which values to return.

        :param spine: (Optional) The spine to join against, as a dataframe.
            If present, the returned data frame will contain rollups for all (join key, temporal key)
            combinations that are required to compute a full frame from the spine. If spine is not
            specified, it'll return a dataframe of  feature values in the specified time range.
        :param timestamp_key: (Optional) Name of the time column in spine.
            If unspecified, will default to the time column of the spine if there is only one present.
        :param entities: (Optional) A DataFrame that is used to filter down feature values.
            If specified, this DataFrame should only contain join key columns.
        :param start_time: (Optional) The interval start time from when we want to retrieve features.
        :param end_time:  (Optional) The interval end time until when we want to retrieve features.
        :param save_dataset: (Optional) set to True to persist DataFrame as a Dataset object.
        :param save_as: (Optional) name to save the DataFrame as. Not applicable when save_dataset=False.
            If unspecified and save_dataset=True, a name will be generated.

        :return: A Tecton DataFrame with features values.
        """

        return self._get_historical_features(
            spine,
            timestamp_key,
            start_time,
            end_time,
            entities,
            from_source=False,
            save_dataset=save_dataset,
            save_as=save_as,
        )

    @sdk_public_method
    def get_feature_vector(
        self,
        join_keys: Optional[Mapping[str, Union[int, np.int_, str, bytes]]] = None,
        include_join_keys_in_response: bool = False,
    ) -> FeatureVector:
        """
        Returns a single Tecton FeatureVector from the Online Store.

        :param join_keys: Join keys of the enclosed FeatureTable.
        :param include_join_keys_in_response: Whether to include join keys as part of the response FeatureVector.

        :return: A FeatureVector of the results.
        """
        # doing checks here instead of get_online_features in order to provide the correct error messages
        if not self._proto.feature_table.online_enabled:
            raise errors.UNSUPPORTED_OPERATION(
                "get_feature_vector", "online_serving_enabled was not defined for this Feature View."
            )
        if join_keys is None:
            raise errors.FS_GET_FEATURE_VECTOR_REQUIRED_ARGS
        return self.get_online_features(join_keys, include_join_keys_in_response)

    @sdk_public_method
    def get_online_features(
        self,
        join_keys: Mapping[str, Union[int, np.int_, str, bytes]],
        include_join_keys_in_response: bool = False,
    ) -> FeatureVector:
        """
        Returns a single Tecton FeatureVector from the Online Store.

        :param join_keys: Join keys of the enclosed FeatureTable.
        :param include_join_keys_in_response: Whether to include join keys as part of the response FeatureVector.

        :return: A FeatureVector of the results.
        """
        if not self._proto.feature_table.online_enabled:
            raise errors.UNSUPPORTED_OPERATION(
                "get_online_features", "online_serving_enabled was not defined for this Feature Table."
            )
        if not isinstance(join_keys, dict):
            raise errors.INVALID_JOIN_KEYS_TYPE(type(join_keys))

        return _QueryHelper(self._proto.fco_metadata.workspace, feature_package_name=self.name).get_feature_vector(
            join_keys, include_join_keys_in_response, request_context_map=None, request_context_schema=None
        )

    @sdk_public_method
    def preview(self, limit=10, time_range: Optional[pendulum.Period] = None):
        """
        Shows a preview of the FeatureTable's features. Random, unique join_keys are chosen to showcase the features.

        :param limit: (Optional, default=10) The number of rows to preview.
        :param time_range: (Optional) Time range to collect features from. Will default to recent data (past 2 days).

        :return: A Tecton DataFrame.
        """
        raise NotImplementedError()

    @sdk_public_method
    def ingest(self, df: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame]):
        """
        Ingests a Dataframe into the FeatureTable.

        :param df: The Dataframe to be ingested. Has to conform to the FeatureTable schema.
        """
        get_upload_info_request = GetNewIngestDataframeInfoRequest()
        get_upload_info_request.feature_definition_id.CopyFrom(self._id_proto)
        upload_info_response = metadata_service.instance().GetNewIngestDataframeInfo(get_upload_info_request)
        df_path = upload_info_response.df_path
        upload_url = upload_info_response.signed_url_for_df_upload

        # We write in the native format and avoid converting Pandas <-> Spark due to partially incompatible
        # type system, in specifically missing Int in Pandas
        if isinstance(df, pyspark.sql.dataframe.DataFrame):
            self._upload_df_spark(df_path, df)
        else:
            self._check_types_and_upload_df_pandas(upload_url, df_path, df)

        ingest_request = IngestDataframeRequest()
        ingest_request.workspace = self.workspace
        ingest_request.feature_definition_id.CopyFrom(self._id_proto)
        ingest_request.df_path = df_path
        response = metadata_service.instance().IngestDataframe(ingest_request)

    def _check_types_and_upload_df_pandas(self, upload_url: str, df_path: str, df: pandas.DataFrame):
        """
        Since Pandas doesn't have Integer type, only Long, we automatically cast Long columns
        to Ints (when FP schema has the same column as Integer), while leaving rest of the types in place.
        """
        tc = TectonContext.get_instance()
        spark = tc._spark
        spark_df = spark.createDataFrame(df)
        df_columns = Schema.from_spark(spark_df.schema).column_name_types()
        fp_columns = self._view_schema.column_name_types()
        converted_columns = []
        converted_df_schema = StructType()
        for df_column in df_columns:
            if df_column[1] == "long" and (df_column[0], "integer") in fp_columns:
                converted_columns.append(df_column[0])
                converted_df_schema.add(df_column[0], "integer")
            else:
                converted_df_schema.add(df_column[0], df_column[1])

        if converted_columns:
            logger.warning(
                f"Tecton is casting field(s) {', '.join(converted_columns)} to type Integer (was type Long). "
                f"To remove this warning, use a Long type in the FeatureTable schema."
            )
            converted_df = spark.createDataFrame(df, schema=converted_df_schema)
            self._upload_df_spark(df_path, converted_df)
        else:
            self._upload_df_spark(df_path, spark_df)
            # Theoretically a faster way to upload native pandas DF, compared to converting to Spark DF first.
            # Currently disabled due to dependency version incompatibility between numpy==1.21.0 in DB notebooks
            # with pyarrow==0.13.0 that we pin. Can't upgrade pyarrow due to incompatibility with
            # Spark 2, see https://tecton-ai.phacility.com/D8180#141519.
            # self._upload_df_pandas(upload_url, df)

    def _upload_df_spark(self, df_path: str, df: pyspark.sql.dataframe.DataFrame):
        df.write.parquet(df_path)

    def _upload_df_pandas(self, upload_url: str, df: pandas.DataFrame):
        out_buffer = BytesIO()
        df.to_parquet(out_buffer, index=False)

        # Maximum 1GB per ingestion
        if out_buffer.__sizeof__() > 1000000000:
            raise errors.FP_PUSH_DF_TOO_LARGE

        r = requests.put(upload_url, data=out_buffer.getvalue())
        if r.status_code != 200:
            raise errors.PUSH_UPLOAD_FAILED(r.reason)


@sdk_public_method
def get_feature_table(ft_reference: str, workspace_name: Optional[str] = None) -> FeatureTable:
    """
    Fetch an existing :class:`FeatureTable` by name.

    :param ft_reference: Either a name or a hexadecimal feature table ID.
    :returns: :class:`FeatureTable`
    """
    request = GetFeatureViewRequest()
    request.version_specifier = ft_reference
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().GetFeatureView(request)
    if not response.HasField("feature_view"):
        raise errors.FCO_NOT_FOUND(FeatureTable, ft_reference)

    if not response.feature_view.HasField("feature_table"):
        raise errors.FCO_NOT_FOUND_WRONG_TYPE(FeatureTable, ft_reference, "get_feature_table")

    return FeatureTable(response.feature_view)
