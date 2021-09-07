# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module containing abstract class for DNNForecastWrapper and DNNParams."""
import copy
import logging
import sys

import azureml.dataprep as dprep
import numpy as np
import pandas as pd
import torch
from typing import Any, Dict, List, Optional, Union
from torch.utils.data import DataLoader

from ..constants import ForecastConstant
from ..datasets.timeseries_datasets import TimeSeriesDataset, TimeSeriesInferenceDataset
from ..types import DataInputType, FeaturizerType, TargetInputType
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TimeseriesNothingToPredict, \
    ForecastHorizonExceeded
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.exceptions import ClientException, DataException
from azureml.contrib.automl.dnn.forecasting.wrapper import _wrapper_util
from forecast.callbacks import CallbackList


class DNNParams:
    """This class is used in storing the DNN parameters for various forecast models."""

    def __init__(self,
                 required: List[str],
                 params: Dict[str, Any],
                 defaults: Optional[Dict[str, Any]] = None):
        """Initialize the object with required, default and passed in parameters.

        :param required: Required parameters for this Model, used in validation.
        :param params:  parameters passed.
        :param defaults: Default parameter if a required parameter is not passed.
        """
        self._required = required.copy() if required else {}
        self._params = params.copy() if params else {}
        self._data_for_inference = None
        self._init_defaults_for_missing_required_parameters(defaults if defaults else {})

    def set_parameter(self, name: str, value: Any) -> None:
        """Set the parameter with the passed in value.

        :param name: name of the parameter to set/update.
        :param value: value to set.
        :return: None
        """
        self._params[name] = value

    def _init_defaults_for_missing_required_parameters(self, defaults) -> None:
        """Set default values for missing required parameters.

        :return:
        """
        for name in self._required:
            if name not in self._params:
                if name in defaults:
                    self._params[name] = defaults[name]
                else:
                    raise ClientException("Required parameter '{0}' is missing.".format(name), has_pii=False)

    def get_value(self, name: str, default_value: Any = None) -> Any:
        """Get the value from the parameter or default dictionary.

        :param name: name of the parameter to get the values for.
        :param default_value: default value to use in case param is unset or not found
        :return:
        """
        if name in self._params:
            value = self._params.get(name)
            if value is None:
                value = default_value
            return value
        return default_value

    def __str__(self) -> str:
        """Return the string printable representation of the DNNParams.

        :return:
        """
        return str(self._params)


class DNNForecastWrapper(torch.nn.Module):
    """This is the abstract class for Forecast DNN Wrappers."""

    def __init__(self):
        """Initialize with defaults."""
        super().__init__()
        self.input_channels = None
        self.params = None
        self.output_channels = 1
        self._pre_transform = None
        self._sample_transform = None
        self.forecaster = None
        self._data_for_inference = None

    def train(self, n_epochs: int, X: DataInputType = None, y: DataInputType = None,
              X_train: DataInputType = None, y_train: DataInputType = None,
              X_valid: DataInputType = None, y_valid: DataInputType = None,
              logger: logging.Logger = None,
              featurizer: Union[FeaturizerType] = None) -> None:
        """Start the DNN training.

        :param n_epochs: number of epochs to try.
        :param X: full set of data for training.
        :param y: fullsetlabel for training.
        :param X_train: training data to use.
        :param y_train: validation data to use.
        :param X_valid: validation data to use.
        :param y_valid: validation target  data to use.
        :param logger: logger
        :param featurizer: The trained featurizer.
        :return: Nothing, the model is trained.
        """
        raise NotImplementedError

    def predict(self, X: DataInputType, y: DataInputType, n_samples: int) -> np.ndarray:
        """Return the predictions for the passed in X and y values.

        :param X: data values
        :param y: label for look back and nan for the rest.
        :param n_samples:  number samples to be retured with each prediction.
        :return: a tuple containing one dimentional prediction of ndarray and tranformed X dataframe.
        """
        raise NotImplementedError

    def get_lookback(self):
        """Return the lookback."""
        raise NotImplementedError

    def forecast(self, X: DataInputType, y: Optional[TargetInputType] = None) -> tuple:
        """Return the predictions for the passed in X and y values.

        :param X: data values
        :param y: label for look back and nan for the rest.
        :param n_samples:  number samples to be retured with each prediction.
        :return: a ndarray of samples X rows X horizon
        """
        Validation.validate_value(X, 'X')
        Validation.validate_type(X, 'X', (pd.DataFrame, dprep.Dataflow))
        horizon = self.params.get_value(ForecastConstant.Horizon)
        looback = self.get_lookback()
        saved_data = self._data_for_inference
        X, y = _wrapper_util.convert_X_y_to_pandas(X, y)
        X = X.copy()
        y = pd.DataFrame([np.nan] * X.shape[0]) if y is None else y.copy()
        self._check_required_prediction_horizon(X, y)
        X_transformed, y_transformed = _wrapper_util.transform_data(self._pre_transform, X, y)
        inference_dataset = TimeSeriesInferenceDataset(X_transformed, y_transformed, saved_data, horizon, looback,
                                                       None, True, self._sample_transform, **self.dataset_settings)
        y_pred_horizon = self._predict(inference_dataset)
        merged_prediction_df = inference_dataset.merge_results(X, y, y_pred_horizon)
        # Returns a vector of predictions and an index for the prediction.
        # classical returns the full dataframe not just index.
        y_return_value = merged_prediction_df[
            ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN].values
        index_for_return_value = merged_prediction_df
        return y_return_value, index_for_return_value

    def _check_required_prediction_horizon(self, X: pd.DataFrame, y: pd.DataFrame) -> None:
        """Check the required prediction horizon for all grains in a dataset."""
        # Get dataset metadata
        settings = self.dataset_settings
        grains = None
        if ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES in settings:
            grains = settings[ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES]
        time_column = settings[ForecastConstant.time_column_name]
        horizon = self.params.get_value(ForecastConstant.Horizon)

        # Build combined dataframe
        df = X.copy(deep=False)
        df[ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y.values

        # Validate required prediction horizon
        if grains is None:
            self._check_required_prediction_horizon_for_one_grain(df, horizon, time_column)
        else:
            groupby = df.groupby(grains)
            for grain in groupby.groups:
                grain_df = groupby.get_group(grain)
                self._check_required_prediction_horizon_for_one_grain(grain_df, horizon, time_column)

    @classmethod
    def _check_required_prediction_horizon_for_one_grain(
            cls, df: pd.DataFrame, horizon: int, time_column: str) -> None:
        target_column = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        if np.any(np.isnan(df[target_column])):
            forecast_origin = min(df[df[target_column] is None or np.isnan(df[target_column])][time_column])
        else:
            raise DataException._with_error(AzureMLError.create(TimeseriesNothingToPredict))
        if df[df[time_column] >= forecast_origin].shape[0] > horizon:
            raise DataException._with_error(AzureMLError.create(ForecastHorizonExceeded, target="horizon"))

    def parse_parameters(self) -> DNNParams:
        """Parse parameters from command line.

        :return: returns the  DNN  param object from the command line arguments
        """
        raise NotImplementedError

    def init_model(self, settings: dict = None) -> None:
        """Initialize the model using the command line parse method.

        :param settings: automl settings such as lookback and horizon etc.
        :return:
        """
        self.params = self.parse_parameters()
        for item in settings if settings else {}:
            self.params.set_parameter(item, settings[item])

    def set_transforms(self, input_channels: int, sample_transform: Any = None) -> None:
        """Set the the training data set transformations and channels.

        :param input_channels: Number of features in tne dataset.
        :param sample_transform: transformations applied as part of tcn dataset processing.
        :return:
        """
        if self.input_channels is None:
            self.input_channels = input_channels

        if self._sample_transform is None:
            self._sample_transform = sample_transform

    def create_data_loader(self, ds: TimeSeriesDataset, batch_size: int) -> DataLoader:
        """Create the dataloader from time series dataset.

        :param ds: TimeseriesDataset
        :param batch_size:  batch size for the training.
        :return:
        """
        self.set_transforms(ds.feature_count(), ds.sample_transform)

        num_cpu = self._get_num_workers_data_loader(dataset=ds)

        return DataLoader(
            ds,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_cpu,
            pin_memory=True)

    @staticmethod
    def _get_num_workers_data_loader(dataset: TimeSeriesDataset) -> int:
        """Get count of number of workers to use for loading data.

        :param dataset: TimeseriesDataset that will be loaded with num workers.
        :return: returns number of workers to use
        """
        # on win using num_workers causes spawn of processes which involves pickling
        # loading data in main process is faster in that case
        if sys.platform == 'win32':
            return 0
        num_cpu_core = None
        try:
            import psutil
            num_cpu_core = psutil.cpu_count(logical=False)
        except Exception:
            import os
            num_cpu_core = os.cpu_count()
            if num_cpu_core is not None:
                # heuristics assuming 2 hyperthreaded logical cores per physical core
                num_cpu_core /= 2

        if num_cpu_core is None:
            # Default to 0 to load data in main thread memory
            return 0
        else:
            return int(num_cpu_core)

    @staticmethod
    def get_arg_parser_name(arg_name: str):
        """Get the argument name needed for arg parse.(prefixed with --).

        :param arg_name: argument name to convert to argparser format.
        :return:

        """
        return "--{0}".format(arg_name)

    @property
    def dataset_settings(self):
        """Get data settings for data that model is trained on."""
        settings = self.params.get_value(ForecastConstant.dataset_settings)
        return settings if settings else {}

    @property
    def name(self):
        """Name of the Model."""
        raise NotImplementedError

    def __getstate__(self) -> Dict[str, Any]:
        """
        Get state pickle-able objects.

        :return: state
        """
        state = dict(self.__dict__)

        # This is assuming that model is used for inference.
        # callbacks need to be created and set on the forecaster for retraining
        # with the new dataset
        state['loss_dict'] = {}
        state['optimizer_dict'] = {}
        if self.forecaster:
            if self.forecaster.loss:
                state['loss_dict'] = self.forecaster.loss.state_dict()
            if self.forecaster.optimizer:
                state['optimizer_dict'] = self.forecaster.optimizer.state_dict()
        state['forecaster'] = None
        return state

    def __setstate__(self, state) -> None:
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        self.__dict__.update(state)
