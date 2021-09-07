# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, List, Any, Callable, Set, Tuple
import logging
import os

from joblib import Parallel, delayed, parallel_backend
import pandas as pd

from azureml._common._error_definition import AzureMLError
from azureml._tracing._tracer_factory import get_tracer
from azureml.automl.core.constants import FeatureType
from azureml.automl.core.featurization.featurizationconfig import FeaturizationConfig
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesDfMultiFrequenciesDiff,
    TimeseriesDsFreqLessThenFcFreq
)
from azureml.automl.core.shared.constants import TimeSeries, TimeSeriesInternal, TimeSeriesWebLinks
from azureml.automl.core.shared.forecasting_exception import (
    ForecastingConfigException,
    ForecastingDataException)
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.data import TabularDataset
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.runtime._automl_job_phases.utilities import PhaseUtil
from azureml.train.automl.runtime._automl_job_phases.worker_initiator import get_worker_variables
from azureml.train.automl.runtime._partitioned_dataset_utils import _get_dataset_for_grain

from azureml.automl.runtime._freq_aggregator import _get_frequency_nanos
from azureml.automl.runtime._grain_preparer import _preprocess_grain, _validate_grain_by_dataset
from azureml.automl.runtime._grain_stat_generator import _get_grain_stat, GrainStatistics
from azureml.automl.runtime.column_purpose_detection import _time_series_column_helper
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.featurizer.transformer.timeseries.forecasting_heuristic_utils import frequency_based_lags

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


class DistributedPreparationPhase:
    """AutoML job phase that prepares the data."""

    @staticmethod
    def run(workspace_getter: Callable[..., Any],
            experiment_name: str,
            parent_run_id: str,
            automl_settings: AzureAutoMLSettings,
            training_dataset: TabularDataset,
            validation_dataset: TabularDataset,
            parallel_backend_name: str='dask') -> None:

        """
        We do following this in this function
        We do grain statistics calculation in distributed way
        We do make some centralized decisions and stat summary calculations based on gathered statistics
        We do some centralized validations that cant be done in distributed way
        We then prepare data in distributed way (fixing frequency, aggregating and padding short series)
        We then invoke grain by grain validation in distributed way
        We then do train/valid split
        """

        PhaseUtil.log_with_memory("Beginning distributed preparation")

        grain_stats = None
        with parallel_backend(parallel_backend_name):
            grain_stats = Parallel(n_jobs=-1)(delayed(_get_grain_stat)(
                _get_dataset_for_grain(grain_key_value, training_dataset),
                grain_key_value,
                automl_settings,
            ) for grain_key_value in training_dataset.get_partition_key_values())

        # we now have stat for all grains. Validate and consolidate
        new_frequency, max_horizon, should_aggregate = validate_and_infer_global(automl_settings, grain_stats)
        if validation_dataset is None:
            if should_aggregate and (_get_frequency_nanos(automl_settings.freq) < _get_frequency_nanos(new_frequency)):
                forecast_freqstr = \
                    automl_settings.freq if isinstance(automl_settings.freq, str) else automl_settings.freq.freqstr
                raise ForecastingConfigException._with_error(
                    AzureMLError.create(
                        TimeseriesDsFreqLessThenFcFreq, target=TimeSeries.FREQUENCY,
                        reference_code=ReferenceCodes._FORECASTING_PARAM_USER_FREQ_DISTRIBUTED,
                        data_freq=new_frequency.freqstr,
                        forecast_freq=forecast_freqstr,
                        freq_doc=TimeSeriesWebLinks.FORECAST_PARAM_DOCS
                    )
                )

            start_times = [grain_stat.start_time for grain_stat in grain_stats]
            prepared_data_dir = '{}_{}_prepared'.format(experiment_name, parent_run_id)

            # Get aggregate column types. Do this by taking the first 10000 rows and assume
            # it is representative of the dataset.
            data_subset = training_dataset.take(10000).to_pandas_dataframe()

            featurization_config = FeaturizationConfig()
            if isinstance(automl_settings.featurization, dict):
                # If user passed in a featurization config, update default with their configuration.
                featurization_config = featurization_config._from_dict(automl_settings.featurization)

            # These should be cached as StatsAndColumnPurpose
            numeric_columns = _time_series_column_helper.get_numeric_columns(
                data_subset, automl_settings.time_column_name,
                automl_settings.grain_column_names, featurization_config)  # type: Set[Any]
            datetime_columns = _time_series_column_helper.get_datetime_columns(
                data_subset, automl_settings.time_column_name,
                automl_settings.grain_column_names, featurization_config)  # type: Set[Any]

            current_purposes = featurization_config.column_purposes or {}

            for col in numeric_columns:
                if col not in current_purposes and col != automl_settings.label_column_name:
                    current_purposes[col] = FeatureType.Numeric
            for col in datetime_columns:
                if col not in current_purposes:
                    current_purposes[col] = FeatureType.DateTime

            featurization_config.column_purposes = current_purposes
            # TODO: make sure this is saved for featurization phase (and onward)
            # if aggregation is enabled for now we cannot persist this VSO: 1326498
            automl_settings.featurization = featurization_config.__dict__

            with logging_utilities.log_activity(logger=logger, activity_name='DistributedPreparation'):
                with parallel_backend(parallel_backend_name):
                    Parallel(n_jobs=-1)(delayed(_preprocess_one_grain)(
                        workspace_getter,
                        prepared_data_dir,
                        parent_run_id,
                        _get_dataset_for_grain(grain_key_value, training_dataset),
                        grain_key_value,
                        new_frequency,
                        max_horizon,
                        start_time,
                        automl_settings,
                        should_aggregate
                    ) for grain_key_value, start_time in zip(training_dataset.get_partition_key_values(), start_times))

            expr_store = ExperimentStore.get_instance()
            expr_store.data.partitioned.save_prepared_train_dataset(
                workspace_getter(),
                prepared_data_dir + "_train",
                training_dataset.partition_keys
            )
            expr_store.data.partitioned.save_prepared_valid_dataset(
                workspace_getter(),
                prepared_data_dir + "_validation",
                training_dataset.partition_keys
            )
        else:
            with logging_utilities.log_activity(logger=logger, activity_name='DistributedValidation'):
                with parallel_backend(parallel_backend_name):
                    Parallel(n_jobs=-1)(delayed(_validate_grain_by_dataset)(
                        _get_dataset_for_grain(grain_key_value, training_dataset),
                        _get_dataset_for_grain(grain_key_value, validation_dataset),
                        automl_settings
                    ) for grain_key_value in training_dataset.get_partition_key_values())

    PhaseUtil.log_with_memory("Ending distributed preparation")


def _preprocess_one_grain(
    workspace_getter: Callable[..., Any],
    prepared_data_data_dir: str,
    parent_run_id: str,
    training_dataset_for_grain: TabularDataset,
    grain_keys_values: Dict[str, Any],
    new_frequnecy: pd.DateOffset,
    max_horizon: int,
    start_time: pd.Timestamp,
    automl_settings: AzureAutoMLSettings,
    should_aggregate: bool
) -> None:

    default_datastore_for_worker, workspace_for_worker, expr_store_for_worker = get_worker_variables(
        workspace_getter, parent_run_id)
    os.makedirs(prepared_data_data_dir, exist_ok=True)

    # load pandas dataframe for one grain
    train_X_grain = training_dataset_for_grain.to_pandas_dataframe()

    # transform one grain
    train_prepared_data, validation_prepared_data = _preprocess_grain(
        train_X_grain,
        new_frequnecy,
        max_horizon,
        start_time,
        automl_settings,
        should_aggregate
    )
    for prepared_data, split in \
            zip([train_prepared_data, validation_prepared_data], ['train', 'validation']):
        # write one grain to local file
        # drop the grain columns since they will be part of the path and hence
        # they will be reconstructed as part of reading partitioned dataset
        prepared_data.reset_index(inplace=True, drop=True)
        prepared_data.drop(columns=automl_settings.grain_column_names, inplace=True)
        grain_keys_values_str = '-'.join([str(v) for v in grain_keys_values.values()])
        prepared_file_name = '{}-{}.parquet'.format(split, grain_keys_values_str)
        prepared_file_path = '{}/{}'.format(prepared_data_data_dir, prepared_file_name)
        prepared_data.to_parquet(prepared_file_path)

        # construct the path to which data will be written to on the default blob store
        target_path_array = ['_'.join([prepared_data_data_dir, split])]
        for val in grain_keys_values.values():
            target_path_array.append(str(val))
        target_path = '/'.join(target_path_array)

        # upload data to default store
        expr_store_for_worker.data.partitioned.write_file(prepared_file_path, target_path)
        logger.info("prepared one grain and uploaded data")


def validate_and_infer_global(
    automl_settings: AzureAutoMLSettings,
    grain_stats: List[GrainStatistics]
) -> Tuple[pd.DateOffset, int, bool]:
    """
    This method is runs on driver node and is responsible for few things
    Validate global statistics -- such as all grains have same frequency
    Summarize global statistics
    Make global decisions such as following
        -- whether there is need to prepare data (either it is already good OR cant be fixed)
        -- what is common inferred frequency
    """
    frequencies_not_nan = [grain_stat.frequency for grain_stat in grain_stats if grain_stat.frequency is not None]
    unique_frequencies = list(set(frequencies_not_nan))
    if len(unique_frequencies) != 1:
        raise ForecastingDataException._with_error(
            AzureMLError.create(TimeseriesDfMultiFrequenciesDiff, target='freq',
                                reference_code=ReferenceCodes._DIST_DATA_PREP_MULTI_FREQUENCIES_DIFF))

    should_aggregate = automl_settings.target_aggregation_function is not None and automl_settings.freq is not None

    new_frequnecy = unique_frequencies[0]
    max_horizon = frequency_based_lags(new_frequnecy)
    if max_horizon == 0:
        max_horizon = TimeSeriesInternal.MAX_HORIZON_DEFAULT
    return new_frequnecy, max_horizon, should_aggregate
