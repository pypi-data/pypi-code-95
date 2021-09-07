# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, Tuple, Union

import azureml.automl.runtime.featurizer.transformer.timeseries as automl_transformer
import numpy as np
import pandas as pd
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.runtime import _ml_engine
from azureml.contrib.automl.dnn.forecasting.constants import ForecastConstant
from azureml.contrib.automl.dnn.forecasting.types import DataInputType, FeaturizerType, TargetInputType


def transform_data(
        featurizer: FeaturizerType, X_df: pd.DataFrame,
        y_df: Optional[Union[np.ndarray, pd.DataFrame, pd.Series]]) -> Tuple[
            pd.DataFrame, Optional[pd.DataFrame]]:
    """Transform the raw data."""
    y_df = y_df.values if isinstance(y_df, (pd.DataFrame, pd.Series)) else y_df
    transformed_data = featurizer.transform(X_df, y_df).sort_index()
    return split_transformed_data_into_X_y(transformed_data)


def split_transformed_data_into_X_y(transformed_data: pd.DataFrame) -> Tuple[
        pd.DataFrame, Optional[pd.DataFrame]]:
    """Split transformed raw data into X and y."""
    X_df, y_df = transformed_data, None
    if ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN in X_df:
        y_df = X_df[[ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN]]
        X_df = X_df.drop(columns=[ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN])
    return X_df, y_df


def train_featurizer(X_df: pd.DataFrame, y_df: Optional[pd.DataFrame], dataset_settings: dict) -> None:
    """Create a timeseries transform which is applied before data is passed to DNN."""
    if ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES not in dataset_settings:
        dataset_settings[ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES] = None
    if isinstance(dataset_settings.get(ForecastConstant.Horizon), str):
        dataset_settings[ForecastConstant.Horizon] = ForecastConstant.auto

    feat_config = FeaturizationConfig()
    if dataset_settings.get("featurization_config"):
        feat_config = dataset_settings.get("featurization_config")
        del dataset_settings["featurization_config"]
    (
        forecasting_pipeline,
        ts_param_dict,
        lookback_removed,
        time_index_non_holiday_features
    ) = _ml_engine.suggest_featurizers_timeseries(
        X_df,
        y_df,
        feat_config,
        dataset_settings,
        automl_transformer.TimeSeriesPipelineType.FULL
    )

    featurizer = automl_transformer.TimeSeriesTransformer(
        forecasting_pipeline,
        automl_transformer.TimeSeriesPipelineType.FULL,
        feat_config,
        time_index_non_holiday_features,
        lookback_removed,
        **ts_param_dict
    )
    featurizer.fit(X_df, y_df)

    return featurizer


def convert_X_y_to_pandas(X: DataInputType, y: Optional[TargetInputType]) -> Tuple[
        pd.DataFrame, Optional[pd.DataFrame]]:
    """Convert X and y to pandas DataFrames."""
    if isinstance(X, pd.DataFrame):
        X_df = X
    else:
        X_df = X.to_pandas_dataframe(extended_types=True)

    if isinstance(y, np.ndarray) or isinstance(y, pd.Series):
        y_df = pd.DataFrame(y)
    elif isinstance(y, pd.DataFrame) or y is None:
        y_df = y
    else:
        y_df = y.to_pandas_dataframe(extended_types=True)

    return X_df, y_df
