# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Set, Any

import pandas as pd

from azureml.data import TabularDataset
from azureml.automl.core.constants import FeatureType
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.constants import TimeSeriesInternal
from azureml.automl.core.shared.types import GrainType
from azureml.automl.runtime._data_definition import RawExperimentData
from azureml.automl.runtime._freq_aggregator import _aggregate_one_grain, _get_mode_col_name
from azureml.automl.runtime._ml_engine import timeseries_ml_engine
from azureml.automl.runtime._time_series_data_config import TimeSeriesDataConfig
from azureml.automl.runtime.frequency_fixer import _correct_start_time, fix_frequency_one_grain
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings


def _preprocess_grain(
    X: pd.DataFrame,
    new_frequnecy: pd.offsets,
    max_horizon: int,
    start_time: pd.Timestamp,
    automl_settings: AzureAutoMLSettings,
    should_aggregate: bool,
) -> pd.DataFrame:
    """
    preprocess includes 3 steps
    1. preparation
    2. splitting
    3. validation
    """
    prepared_grain_data = _prepare_grain(
        X,
        automl_settings,
        should_aggregate,
        new_frequnecy,
        start_time
    )
    grain_train_data, grain_validation_data = _split_grain(prepared_grain_data, max_horizon, automl_settings)
    if should_aggregate:
        # reset the featurization config in cases of aggregation VSO: 1326498
        automl_settings.featurization = FeaturizationConfig().__dict__
    _validate_grain(grain_train_data, grain_validation_data, automl_settings)
    return grain_train_data, grain_validation_data


def _validate_grain_by_dataset(grain_train_dataset: TabularDataset,
                               grain_validation_dataset: TabularDataset,
                               automl_settings: AzureAutoMLSettings) -> None:
    _validate_grain(grain_train_dataset.to_pandas_dataframe(),
                    grain_validation_dataset.to_pandas_dataframe(),
                    automl_settings)


def _validate_grain(grain_train_data: pd.DataFrame,
                    grain_validation_data: pd.DataFrame,
                    automl_settings: AzureAutoMLSettings) -> None:

    grain_train_X = grain_train_data.copy(deep=True)
    grain_train_y = grain_train_X.pop(automl_settings.label_column_name).values

    grain_validation_X = grain_validation_data.copy(deep=True)
    grain_validation_y = grain_validation_X.pop(automl_settings.label_column_name).values

    raw_experiment_Data = RawExperimentData(X=grain_train_X,
                                            y=grain_train_y,
                                            X_valid=grain_validation_X,
                                            y_valid=grain_validation_y)
    timeseries_ml_engine.validate_timeseries(raw_experiment_Data, automl_settings)


def _split_grain(grain_data: pd.DataFrame,
                 max_horizon: int,
                 automl_settings: AzureAutoMLSettings) -> pd.DataFrame:

    grain_data[automl_settings.time_column_name] = pd.to_datetime(grain_data[automl_settings.time_column_name])
    grain_data.sort_values(by=automl_settings.time_column_name, inplace=True)
    grain_train_data = grain_data.head(len(grain_data) - max_horizon)
    grain_validation_data = grain_data.tail(max_horizon)
    return grain_train_data, grain_validation_data


def _prepare_grain(
    X: pd.DataFrame,
    automl_settings: AzureAutoMLSettings,
    should_aggregate: bool,
    new_frequnecy: pd.offsets,
    start_time: pd.Timestamp
) -> pd.DataFrame:
    """
    Preparation includes 3 kinds of data mutations, each being optional
    1. Fixing non compliant points
    2. Aggregate
    3. Pad short grains
    #1 and #2 are mutually exclusive
    """
    # Check if aggregation enabled
    # if yes, do agg
    # if no, fix
    # frequency_fixer.py L:611-624
    if should_aggregate:
        y_grain = X[automl_settings.label_column_name].values
        X_grain_no_target = X.copy(deep=True)
        X_grain_no_target.pop(automl_settings.label_column_name)
        ts_config = TimeSeriesDataConfig.from_settings(X_grain_no_target, y_grain, automl_settings)

        # If we are here we must have an aggregation funciton
        Contract.assert_value(ts_config.target_aggregation_function, "target_aggregation_function")
        grains = ts_config.data_x[ts_config.time_series_id_column_names].head(1).values.tolist()[0]
        df = _aggregate_grain(ts_config.data_x, ts_config, grains)

        # we must renamed the resulting dataframe's target column back to the original name.
        df.rename({TimeSeriesInternal.DUMMY_TARGET_COLUMN: automl_settings.label_column_name}, axis=1, inplace=True)
        return df
    else:
        return _fix_frequncy(X, automl_settings.time_column_name, new_frequnecy, start_time)


def _fix_frequncy(X: pd.DataFrame,
                  time_column_name: str,
                  new_frequnecy: pd.offsets,
                  start_time: pd.Timestamp) -> pd.DataFrame:
    start_time_corrected = _correct_start_time(X, time_column_name, start_time, new_frequnecy)
    return fix_frequency_one_grain(X, new_frequnecy, start_time_corrected, time_column_name)


def _aggregate_grain(
    X_one: pd.DataFrame,
    time_series_config: TimeSeriesDataConfig,
    time_series_ids: GrainType
) -> pd.DataFrame:
    # TODO: This should be done in a more global place
    X_one.dropna(subset=[time_series_config.time_column_name], inplace=True)
    if X_one.shape[0] == 0:
        # TODO: we really don't need this check here if na time cols are already dropped.
        return pd.DataFrame()

    X_one[TimeSeriesInternal.DUMMY_ORDER_COLUMN] = 1
    # ######## This section only applies at inference time ##############
    # TODO: should we keep this and secion below?
    # Add the phase only if the start time is present in the start_times
    # and it is less then minimal time point in the data set.
    # if start_times is not None and grain in start_times:
    #     data_start = X_one[time_series_config.time_column_name].min()
    #     real_start = start_times[grain]
    #     while real_start > data_start:
    #         real_start -= to_offset(time_series_config.freq)
    #     if real_start < data_start:
    #         # If we have the start time, we have to add the row corresponding to this time to the data set.
    #         time_ix = np.where(X_one.columns.values == time_series_config.time_column_name)[0][0]
    #         pad = [None] * (X_one.shape[1])
    #         pad[time_ix] = real_start
    #         X_one = pd.DataFrame([pad], columns=X_one.columns).append(X_one)
    # #########################################################################
    # Get numeric and datetime columns from featurization
    featurization_config = time_series_config.featurization
    column_purposes = featurization_config.column_purposes or {}
    numeric_columns = set(col_name for col_name, purpose in column_purposes.items() if purpose == FeatureType.Numeric)
    datetime_columns = set(
        col_name for col_name, purpose in column_purposes.items() if purpose == FeatureType.DateTime
    )

    # Set target on dataframe
    X_one[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = time_series_config.data_y

    X_agg = _aggregate_one_grain(X_one, numeric_columns, datetime_columns, time_series_config, time_series_ids)

    # The mode will be applied to the DUMMY_ORDER_COLUMN, so that it will be renamed.
    mode_of_order_col = _get_mode_col_name(TimeSeriesInternal.DUMMY_ORDER_COLUMN)
    if mode_of_order_col in X_agg.columns:
        X_agg.dropna(subset=[mode_of_order_col], inplace=True)
        X_agg.drop(mode_of_order_col, axis=1, inplace=True)

    # ######## This section only applies at inference time ##############
    # TODO: should we keep this and section above?
    # If we have padded the data frame, we could add non desired early date.
    # For example if training set ends 2001-01-25, the frequency is 2D and trainig set
    # starts at 2001-01-26. The aggregation will add the non existing date 2001-01-25
    # to the test set and it will fail the run.
    # But if we have earlier dates, that means a user error and we should not correct it
    # and raise exception in forecast time.
    # if start_times is not None:
    #     min_test_time = X_agg[time_series_config.time_column_name].min()
    #     if grain in start_times and start_times[grain] == min_test_time:
    #         X_agg = X_agg[X_agg[time_series_config.time_column_name] != min_test_time]
    # #########################################################################

    X_agg.reset_index(drop=True, inplace=True)
    return X_agg
