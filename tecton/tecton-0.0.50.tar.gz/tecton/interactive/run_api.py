from datetime import datetime
from typing import Dict
from typing import Optional
from typing import Union

import pandas
import pendulum
from pyspark.sql import DataFrame

import tecton
from tecton._internals import errors
from tecton.tecton_context import TectonContext
from tecton_proto.data import feature_view_pb2
from tecton_spark import data_source_helper
from tecton_spark import materialization_plan
from tecton_spark import time_utils
from tecton_spark.feature_package_view import FeaturePackageOrView
from tecton_spark.id_helper import IdHelper
from tecton_spark.pipeline_helper import get_all_input_keys
from tecton_spark.pipeline_helper import get_all_input_vds_id_map
from tecton_spark.pipeline_helper import pipeline_to_dataframe
from tecton_spark.pipeline_helper import run_mock_pandas_pipeline
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper


def run_batch(
    fv_proto: feature_view_pb2.FeatureView,
    feature_start_time: Optional[Union[pendulum.DateTime, datetime]],
    feature_end_time: Optional[Union[pendulum.DateTime, datetime]],
    mock_inputs: Dict[str, Union[pandas.DataFrame, DataFrame]],
    aggregate_tiles: bool = None,
) -> "tecton.interactive.data_frame.DataFrame":
    spark = TectonContext.get_instance()._spark
    # Validate that mock_inputs' keys.
    input_vds_id_map = get_all_input_vds_id_map(fv_proto.pipeline.root)
    _validate_batch_mock_inputs_keys(mock_inputs, fv_proto)

    feature_time_limits_aligned = _align_times(feature_start_time, feature_end_time, fv_proto)

    # Convert any Pandas dataFrame mock_inputs to Spark, validate schema columns, then apply feature time filter.
    # TODO(raviphol): Consider refactor this under pipeline_helper._node_to_value
    for key in mock_inputs.keys():
        vds = _get_vds_by_id(fv_proto.enrichments.virtual_data_sources, input_vds_id_map[key])

        spark_schema = _get_spark_schema(vds)

        # Covert panda DF to Spark conversion.
        if isinstance(mock_inputs[key], pandas.DataFrame):
            mock_inputs[key] = spark.createDataFrame(mock_inputs[key], spark_schema)

        # TODO(raviphol): Consider using feature_package_utils.validate_df_schema for column and type validation.
        # validate_df_schema(df=mock_inputs[key], view_schema=spark_schema)
        _validate_input_dataframe_schema(input_name=key, dataframe=mock_inputs[key], spark_schema=spark_schema)

        mock_inputs[key] = data_source_helper.apply_partition_and_timestamp_filter(
            df=mock_inputs[key],
            data_source=vds.batch_data_source,
            raw_data_time_limits=feature_time_limits_aligned,
            fwv3=True,
        )

    # Handle aggregate_tile flag
    # TODO(raviphol): Implement aggregate_tile support.
    if aggregate_tiles is not None:
        raise errors.UNSUPPORTED_OPERATION("aggregate_tiles is not supported.")

    # Execute Spark pipeline to get output DataFrame.
    # Verify that mock_inputs and virtual_data_sources works sxs
    return tecton.interactive.data_frame.DataFrame._create(
        pipeline_to_dataframe(
            spark,
            pipeline=fv_proto.pipeline,
            consume_streaming_data_sources=False,
            virtual_data_sources=fv_proto.enrichments.virtual_data_sources,
            transformations=fv_proto.enrichments.transformations,
            feature_time_limits=feature_time_limits_aligned,
            schedule_interval=pendulum.Duration(seconds=fv_proto.materialization_params.schedule_interval.ToSeconds()),
            mock_inputs=mock_inputs,
        )
    )


def run_stream(fv_proto: feature_view_pb2.FeatureView, output_temp_table: str):
    plan = materialization_plan.get_feature_view_stream_materialization_plan(
        TectonContext.get_instance()._spark,
        feature_package_or_view=FeaturePackageOrView.from_fv(fv_proto),
        virtual_data_sources=fv_proto.enrichments.virtual_data_sources,
        new_transformations=fv_proto.enrichments.transformations,
    )
    spark_df = plan.online_store_data_frame

    return spark_df.writeStream.format("memory").queryName(output_temp_table).outputMode("append").start()


def run_ondemand(
    fv_proto: feature_view_pb2.FeatureView, fv_name: str, mock_inputs: Dict[str, Union[pandas.DataFrame, DataFrame]]
) -> "tecton.interactive.data_frame.DataFrame":  # a single row:
    # Validate that all the mock_inputs matchs with FV inputs, and that num rows match across all mock_inputs.
    _validate_ondemand_mock_inputs_keys(mock_inputs, fv_proto)

    # Execute Pandas pipeline to get output DataFrame.
    return tecton.interactive.data_frame.DataFrame._create(
        run_mock_pandas_pipeline(
            name=fv_name,
            pipeline=fv_proto.pipeline,
            transformations=fv_proto.enrichments.transformations,
            mock_inputs=mock_inputs,
        )
    )


# Validate that mock_inputs keys are a subset of virtual data sources.
def _validate_batch_mock_inputs_keys(mock_inputs, fv_proto):
    expected_input_names = get_all_input_keys(fv_proto.pipeline.root)
    if not set(mock_inputs.keys()).issubset(expected_input_names):
        raise errors.FV_INVALID_MOCK_INPUTS(mock_inputs.keys(), expected_input_names)


# Validate that mock_inputs keys are a subset of virtual data sources.
def _validate_ondemand_mock_inputs_keys(mock_inputs, fv_proto):
    expected_input_names = get_all_input_keys(fv_proto.pipeline.root)
    if set(mock_inputs.keys()) != expected_input_names:
        raise errors.FV_INVALID_MOCK_INPUTS(mock_inputs.keys(), expected_input_names)
    # Get num row for all FV mock_inputs, to validate that they match.
    num_rows = [len(mock_inputs[key].index) for key in mock_inputs]
    if len(set(num_rows)) > 1:
        raise TectonValidationError(
            f"Number of rows are not equal across all mock_inputs. Num rows found are {str(num_rows)}."
        )


# Check that schema of each mock inputs matches with virtual data sources.
def _validate_input_dataframe_schema(input_name, dataframe: DataFrame, spark_schema):
    columns = sorted(dataframe.columns)
    expected_column_names = sorted([field.name for field in spark_schema.fields])

    # Validate mock input's schema against expected schema.
    if not expected_column_names == columns:
        raise errors.FV_INVALID_MOCK_INPUT_SCHEMA(input_name, columns, expected_column_names)


def _get_vds_by_id(virtual_data_sources, id: str):
    for vds in virtual_data_sources:
        if IdHelper.to_string(vds.virtual_data_source_id) == id:
            return vds
    return None


# Align feature start and end times with materialization schedule interval.
def _align_times(feature_start_time, feature_end_time, fv_proto):
    # Smart default for feature_end_time if unset.
    feature_end_time = pendulum.now() if feature_end_time is None else feature_end_time
    # Align feature_end_time upward to the nearest materialization schedule interval.
    schedule_interval = time_utils.proto_to_duration(fv_proto.materialization_params.schedule_interval)
    feature_end_time = time_utils.align_time_upwards(feature_end_time, schedule_interval)

    # Smart default for feature_start_time if unset.
    if feature_start_time is None:
        feature_start_time = feature_end_time - schedule_interval
    else:
        # Align feature_start_time downward to the nearest materialization schedule interval.
        feature_start_time = time_utils.align_time_downwards(feature_start_time, schedule_interval)
    return pendulum.period(feature_start_time, feature_end_time)


def _get_spark_schema(vds):
    if vds.HasField("batch_data_source"):
        spark_schema = vds.batch_data_source.spark_schema
    elif vds.HasField("stream_data_source"):
        spark_schema = vds.stream_data_source.spark_schema
    else:
        raise errors.INTERNAL_ERROR("VirtualDataSource is missing a supported data source")
    return SparkSchemaWrapper.from_proto(spark_schema).unwrap()
