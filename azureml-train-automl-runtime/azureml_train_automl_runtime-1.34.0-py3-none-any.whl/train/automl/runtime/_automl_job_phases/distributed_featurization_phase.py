# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import os
from typing import Dict, List, Any, Tuple, Callable, cast

import dask
import pandas as pd
from azureml._tracing._tracer_factory import get_tracer
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared import logging_utilities
from azureml.core import Run
from azureml.data import TabularDataset
from azureml.train.automl import _constants_azureml
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.runtime._automl_job_phases.utilities import PhaseUtil
from azureml.train.automl.runtime._automl_job_phases.worker_initiator import get_worker_variables
from azureml.train.automl.runtime._partitioned_dataset_utils import _get_dataset_for_grain, \
    _to_partitioned_dask_dataframe, _to_dask_dataframe_of_random_grains
from joblib import Parallel, delayed, parallel_backend

from azureml.automl.runtime import _ml_engine as ml_engine, data_context
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.featurizer.transformer import TimeSeriesPipelineType, TimeSeriesTransformer
from azureml.automl.runtime.featurizer.transformer.timeseries._distributed import DistributedTimeseriesTransformer

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


class DistributedFeaturizationPhase:
    """AutoML job phase that featurizes the data."""

    @staticmethod
    def run(workspace_getter: Callable[..., Any],
            current_run: Run,
            parent_run_id: str,
            automl_settings: AzureAutoMLSettings,
            training_dataset: TabularDataset,
            validation_dataset: TabularDataset,
            parallel_backend_name: str = 'dask') -> None:

        PhaseUtil.log_with_memory("Beginning distributed featurization")

        with logging_utilities.log_activity(logger=logger, activity_name='FindingUniqueCategories'):
            categories_by_grain_cols, categories_by_non_grain_cols = _get_categories_by_columns(
                training_dataset,
                automl_settings.grain_column_names)

        with logging_utilities.log_activity(logger=logger, activity_name='BuildTransformer'):
            ts_transformer = _build_transformer(training_dataset,
                                                automl_settings,
                                                categories_by_grain_cols,
                                                categories_by_non_grain_cols)

        featurized_data_dir = '{}_{}_featurized'.format(current_run.experiment.name, parent_run_id)
        grain_key_values = training_dataset.get_partition_key_values()
        with logging_utilities.log_activity(logger=logger, activity_name='DistributedTransformation'):
            with parallel_backend(parallel_backend_name):
                Parallel(n_jobs=-1)(delayed(_transform_one_grain)(
                    workspace_getter,
                    featurized_data_dir,
                    parent_run_id,
                    _get_dataset_for_grain(grain_key_value, training_dataset),
                    _get_dataset_for_grain(grain_key_value, validation_dataset),
                    grain_key_value,
                    ts_transformer,
                    automl_settings.label_column_name,
                    automl_settings.grain_column_names
                ) for grain_key_value in grain_key_values)

        expr_store = ExperimentStore.get_instance()
        # Reload experiment store to update its state. This is required for fetching models
        # trained on individual grains
        # expr_store.unload()
        # expr_store.load()

        # with logging_utilities.log_activity(logger=logger, activity_name='BuildDistributedTransformer'):
        #     distributed_timeseries_transformer = _build_transformer_for_all_grains(
        #         expr_store, automl_settings.grain_column_names, grain_key_values)
        # expr_store.transformers.set_transformers(distributed_timeseries_transformer)

        expr_store.data.partitioned.save_featurized_train_dataset(
            workspace_getter(),
            featurized_data_dir + "_train",
            training_dataset.partition_keys
        )
        expr_store.data.partitioned.save_featurized_valid_dataset(
            workspace_getter(),
            featurized_data_dir + "_validation",
            training_dataset.partition_keys
        )

        # Add placeholder problem info. This is required today by Jasmine.
        current_run.add_properties({
            _constants_azureml.Properties.PROBLEM_INFO: '{}'
        })

        PhaseUtil.log_with_memory("Ending distributed featurization")


def _transform_one_grain(workspace_getter: Callable[..., Any],
                         featurized_data_dir: str,
                         parent_run_id: str,
                         training_dataset_for_grain: TabularDataset,
                         validation_dataset_for_grain: TabularDataset,
                         grain_keys_values: Dict[str, Any],
                         ts_transformer: TimeSeriesTransformer,
                         label_column_name: str,
                         grain_column_names: List[Any]) -> None:

    default_datastore_for_worker, workspace_for_worker, expr_store_for_worker = get_worker_variables(
        workspace_getter, parent_run_id)
    os.makedirs(featurized_data_dir, exist_ok=True)

    # load pandas dataframe for one grain
    train_X_grain = training_dataset_for_grain.to_pandas_dataframe()
    train_y_grain = train_X_grain.pop(label_column_name).values
    validation_X_grain = validation_dataset_for_grain.to_pandas_dataframe()
    validation_y_grain = validation_X_grain.pop(label_column_name).values

    # transform one grain
    train_transformed_data = ts_transformer.fit_transform(train_X_grain, train_y_grain)
    validation_transformed_data = ts_transformer.transform(validation_X_grain, validation_y_grain)

    for transformed_data, split in \
            zip([train_transformed_data, validation_transformed_data], ['train', 'validation']):
        # write one grain to local file
        # drop the grain columns since they will be part of the path and hence
        # they will be reconstructed as part of reading partitioned dataset
        transformed_data.reset_index(inplace=True)
        transformed_data.drop(columns=grain_column_names, inplace=True)
        grain_keys_values_str = '-'.join([str(v) for v in grain_keys_values.values()])
        featurized_file_name = '{}-{}.parquet'.format(split, grain_keys_values_str)
        featurized_file_path = '{}/{}'.format(featurized_data_dir, featurized_file_name)
        transformed_data.to_parquet(featurized_file_path)

        # construct the path to which data will be written to on the default blob store
        target_path_array = ['_'.join([featurized_data_dir, split])]
        for val in grain_keys_values.values():
            target_path_array.append(str(val))
        target_path = '/'.join(target_path_array)

        # upload data to default store
        expr_store_for_worker.data.partitioned.write_file(featurized_file_path, target_path)
        logger.info("transformed one grain and uploaded data")

    # upload fitted pipeline to default datastore
    expr_store_for_worker.transformers.set_by_grain(grain_keys_values, ts_transformer)


def unique_by_partition_columns(partitioned_dataset: TabularDataset,
                                grain_col: str) -> List[Any]:
    categories_for_grain_col = set()
    for key_val in partitioned_dataset.get_partition_key_values():
        categories_for_grain_col.add(key_val[grain_col])
    unique_vals = list(categories_for_grain_col)
    logger.info("Calculated uniques for one grain column")
    return unique_vals


def _get_categories_by_columns(partitioned_dataset: TabularDataset,
                               grain_column_names: List[str]) -> Tuple[Dict[str, List[Any]], Dict[str, List[Any]]]:

    categories_by_grain_cols = {col: pd.Categorical(unique_by_partition_columns(partitioned_dataset,
                                                                                col)).categories
                                for col in grain_column_names}
    PhaseUtil.log_with_memory("Calculated uniques for all grain columns")

    ddf = _to_partitioned_dask_dataframe(partitioned_dataset)
    ddf = ddf.drop(grain_column_names, axis=1)
    categorical_cols = ddf.select_dtypes(['object', 'category', 'bool']).columns

    uniques_delayed = [ddf[col].unique() for col in categorical_cols]
    uniques = dask.compute(*uniques_delayed)
    categories_by_non_grain_cols = {col: pd.Categorical(uniques).categories for col, uniques
                                    in zip(categorical_cols, uniques)}
    PhaseUtil.log_with_memory("Calculated uniques for all non grain columns")

    return categories_by_grain_cols, categories_by_non_grain_cols


def _build_transformer(training_dataset: TabularDataset,
                       automl_settings: AzureAutoMLSettings,
                       categories_by_grain_cols: Dict[str, List[Any]],
                       categories_by_non_grain_cols: Dict[str, List[Any]]) -> TimeSeriesTransformer:

    # We currently subsample 100 grains to handle cases of large number of time series
    # To handle case of large history in addition to large number of time series we need following 2 solutions
    # 1) limit history per time series  2) Keep a tab on memory and limit total rows to fixed count at all costs
    subsampled_grains_ddf = _to_dask_dataframe_of_random_grains(training_dataset, 100)
    subsampled_X = subsampled_grains_ddf.compute()
    subsampled_Y = subsampled_X.pop(automl_settings.label_column_name).values

    data_context_params = data_context.DataContextParams(automl_settings)

    pipeline_type = TimeSeriesPipelineType.FULL
    ts_params = cast(Dict[str, Any], data_context_params.control_params.timeseries_param_dict)
    featurization_config = data_context_params.control_params.featurization
    # Timeseries currently doesn't reject "off" as input and currently converts "auto"/"off" to the object
    # during the featurize_data_timeseries method. Since we bypass that call and call suggest directly, we
    # need to convert from string to object here.
    if isinstance(featurization_config, str):
        featurization_config = FeaturizationConfig()

    (
        forecasting_pipeline,
        timeseries_param_dict,
        lookback_removed,
        time_index_non_holiday_features
    ) = ml_engine.suggest_featurizers_timeseries(
        subsampled_X,
        subsampled_Y,
        featurization_config,
        ts_params,
        pipeline_type,
        categories_by_grain_cols,
        categories_by_non_grain_cols
    )

    ts_transformer = TimeSeriesTransformer(
        forecasting_pipeline,
        pipeline_type,
        featurization_config,
        time_index_non_holiday_features,
        lookback_removed,
        **timeseries_param_dict
    )

    PhaseUtil.log_with_memory("Suggest featurization invoked and transformer pipeline is ready to be fit")
    return ts_transformer


# def _build_transformer_for_all_grains(expr_store, grain_col_names, grain_key_values):
#     distributed_transformer = DistributedTimeseriesTransformer(grain_col_names)
#     for grain_key_value in grain_key_values:
#         transformer = expr_store.transformers.get_by_grain(grain_key_value)
#         distributed_transformer.add_transformer_for_grain(grain_key_value, transformer)
#     return distributed_transformer
