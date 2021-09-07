# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for starting forecast DNN run with passed in model."""
import argparse
import os
from pathlib import Path
import math
import json
from azureml.contrib.automl.dnn.forecasting.types import FeaturizerType
import numpy as np
import pandas as pd
from typing import Any, Optional, Tuple

from ....constants import ForecastConstant
from ....wrapper.forecast_wrapper import DNNForecastWrapper, DNNParams
from ....wrapper.deep4cast_wrapper import Deep4CastWrapper
from ....wrapper.forecast_tcn_wrapper import ForecastTCNWrapper
import azureml.automl.core  # noqa: F401
from azureml.automl.core.systemusage_telemetry import SystemResourceUsageTelemetryFactory
from azureml.automl.core.shared import logging_utilities
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.shared.lazy_azure_blob_cache_store import LazyAzureBlobCacheStore
from azureml.contrib.automl.dnn.forecasting.wrapper import _wrapper_util
from azureml.core.run import Run
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.runtime._azureautomlruncontext import AzureAutoMLRunContext
from azureml.train.automl.runtime._data_preparer import DataPreparerFactory
from azureml.train.automl.runtime._entrypoints.utils.common import get_parent_run_id


# Minimum parameter needed to initiate a training
required_params = [ForecastConstant.model, ForecastConstant.output_dir,
                   ForecastConstant.report_interval, ForecastConstant.config_json]
# get the logger default logger as placeholder.
logger = logging_utilities.get_logger()


def get_model(model_name: str) -> DNNForecastWrapper:
    """Return a `DNNForcastWrapper` corresponding to the passed in model_name.

    :param model_name:  name of the model to train
    :return: gets a wrapped model for Automl DNN Training.
    """
    model_dict = {ForecastConstant.Deep4Cast: Deep4CastWrapper(), ForecastConstant.ForecastTCN: ForecastTCNWrapper()}
    return model_dict[model_name]


def run() -> None:
    """Start the DNN training based on the passed in parameters.

    :return:
    """
    # get command-line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.model), type=str,
                        help='model name', default=ForecastConstant.ForecastTCN)
    parser.add_argument('--output_dir', type=str, help='output directory', default="./outputs")
    parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.num_epochs), type=int,
                        default=25,
                        help='number of epochs to train')
    parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.primary_metric), type=str,
                        default="normalized_root_mean_squared_error", help='primary metric')
    parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.report_interval), type=int,
                        default=1, help='number of epochs to report score')
    parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.config_json), type=str,
                        default=ForecastConstant.config_json_default,
                        help='json representation of dataset and training settings from automl SDK')

    args, unknown = parser.parse_known_args()
    os.makedirs(args.output_dir, exist_ok=True)
    logfile = os.path.join(args.output_dir, ForecastConstant.namespace + '.log')
    Path(logfile).touch()
    logger = logging_utilities.get_logger(ForecastConstant.namespace, logfile)
    args_dict = vars(args)
    params = DNNParams(required_params, args_dict, None)

    model = get_model(params.get_value(ForecastConstant.model))

    run_context = Run.get_context()
    automl_run_context = AzureAutoMLRunContext(run_context)
    settings, automl_settings_obj, datasets_json = _parse_settings_file(params.get_value(ForecastConstant.config_json))

    model.init_model(settings)
    X, y, X_train, y_train, X_valid, y_valid, featurizer = _get_training_data(
        settings, automl_settings_obj, datasets_json, run_context)
    num_epochs = params.get_value(ForecastConstant.num_epochs)

    logging_utilities.log_system_info(logger, prefix_message="[RunId:{}]".format(automl_run_context.run_id))

    telemetry_logger = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(interval=10)

    telemetry_logger.send_usage_telemetry_log(
        prefix_message="[RunId:{}][Starting DNN Training]".format(automl_run_context.run_id),
    )

    logging_utilities.log_system_info(logger, prefix_message="[RunId:{}]".format(automl_run_context.run_id))

    telemetry_logger.send_usage_telemetry_log(
        prefix_message="[RunId:{}][Before DNN Train]".format(automl_run_context.run_id),
    )

    model.train(
        num_epochs, X=X, y=y, X_train=X_train, y_train=y_train, X_valid=X_valid,
        y_valid=y_valid, logger=logger, featurizer=featurizer)

    telemetry_logger.send_usage_telemetry_log(
        prefix_message="[RunId:{}][After DNN Train completed]".format(automl_run_context.run_id),
    )


def _get_distributed_featurization_output(automl_settings_obj: AzureAutoMLSettings, current_run: Run) -> Tuple[
        pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, FeaturizerType]:
    """Get the output (transformed data and featurizer) from the distirbuted feautirzation phase."""
    workspace = current_run.experiment.workspace
    default_datastore = workspace.get_default_datastore()
    cache_store = LazyAzureBlobCacheStore(default_datastore, get_parent_run_id(current_run.id))
    expr_store = ExperimentStore(cache_store, read_only=False)
    expr_store.load()
    train_dataset = expr_store.data.partitioned.get_featurized_train_dataset(workspace)
    train_data = train_dataset.to_pandas_dataframe()
    valid_data = expr_store.data.partitioned.get_featurized_valid_dataset(workspace).to_pandas_dataframe()

    index_cols = [automl_settings_obj.time_column_name]
    if automl_settings_obj.grain_column_names:
        index_cols += automl_settings_obj.grain_column_names

    train_data = train_data.set_index(index_cols).sort_index()
    valid_data = valid_data.set_index(index_cols).sort_index()

    X_train, y_train = _wrapper_util.split_transformed_data_into_X_y(train_data)
    X_valid, y_valid = _wrapper_util.split_transformed_data_into_X_y(valid_data)

    featurizer = expr_store.transformers.get_transformers()

    return X_train, y_train, X_valid, y_valid, featurizer


def _get_training_data(
        settings: dict, automl_settings_obj: AzureAutoMLSettings, datasets_json: str, current_run: Run) -> Tuple[
            Any, Any, Any, Any, Any, Any, FeaturizerType]:
    """Get the training data the form of tuples from dictionary.

    :param settings: Settings for the forecasting problem.
    :param automl_settings_obj: AutoML settings.
    :param dataset_settings: Dataset settings.
    :param current_run: The current run.
    :return: A tuple with transformed train and validation data & the trained featurizer.
    """
    X, y, X_train, y_train, X_valid, y_valid, featurizer = None, None, None, None, None, None, None

    if settings[ForecastConstant.CONSUME_DIST_FEATURIZATION_OUTPUT]:
        X_train, y_train, X_valid, y_valid, featurizer = _get_distributed_featurization_output(
            automl_settings_obj, current_run)
    else:
        X, y, X_train, y_train, X_valid, y_valid, featurizer = _featurize_raw_data(
            settings[ForecastConstant.dataset_settings], automl_settings_obj, datasets_json)

    return X, y, X_train, y_train, X_valid, y_valid, featurizer


def _featurize_raw_data(
        dataset_settings: dict, automl_settings_obj: AzureAutoMLSettings, datasets_json: str) -> tuple:
    """Featurize the raw the data."""
    X_transformed, y_transformed, X_train_transformed, y_train_transformed, X_valid_transformed, y_valid_transformed, \
        featurizer = None, None, None, None, None, None, None

    X, y, X_train, y_train, X_valid, y_valid = _get_raw_data(automl_settings_obj, datasets_json)

    if X_train is not None:
        featurizer = _wrapper_util.train_featurizer(X_train, y_train, dataset_settings)
        X_train_transformed, y_train_transformed = _wrapper_util.transform_data(featurizer, X_train, y_train)
        X_valid_transformed, y_valid_transformed = _wrapper_util.transform_data(featurizer, X_valid, y_valid)
    elif X is not None:
        featurizer = _wrapper_util.train_featurizer(X, y, dataset_settings)
        X_transformed, y_transformed = _wrapper_util.transform_data(featurizer, X, y)

    return X_transformed, y_transformed, X_train_transformed, y_train_transformed, X_valid_transformed, \
        y_valid_transformed, featurizer


def _get_raw_data(automl_settings_obj: AzureAutoMLSettings, datasets_json: str) -> Tuple[
        Optional[pd.DataFrame], Optional[np.ndarray], Optional[pd.DataFrame], Optional[np.ndarray],
        Optional[pd.DataFrame], Optional[np.ndarray]]:
    """Fetch the raw data for the experiment."""
    data_preparer = DataPreparerFactory.get_preparer(datasets_json)
    raw_experiment_data = data_preparer.prepare_raw_experiment_data(automl_settings_obj)
    data_dict = {
        "X": raw_experiment_data.X,
        "y": raw_experiment_data.y,
        "X_valid": raw_experiment_data.X_valid,
        "y_valid": raw_experiment_data.y_valid,
    }

    for data_key in ["X", "X_valid"]:
        if data_dict.get(data_key) is not None and not isinstance(data_dict[data_key], pd.DataFrame):
            data_dict[data_key] = pd.DataFrame(data_dict[data_key], columns=raw_experiment_data.feature_column_names)

    X, y, X_train, y_train, X_valid, y_valid = None, None, None, None, None, None
    if data_dict.get("X_valid") is not None:
        X_valid, y_valid = data_dict["X_valid"], data_dict["y_valid"]
        X_train, y_train = data_dict["X"], data_dict["y"]
    elif "X" in data_dict:
        X, y = data_dict["X"], data_dict["y"]
    return X, y, X_train, y_train, X_valid, y_valid


def _parse_settings_file(file_name: str) -> tuple:
    """Create dprep dataset dict and training setting dict.

    :param file_name: file containing the dataset dprep and other training parameters such as
                      lookback, horizon and time column name.
    :return:
    """
    params = json.load(open(file_name, encoding='utf-8-sig'))
    clean_settings = clean_general_settings_json_parse(params['general.json'])
    general_setting_dict = json.loads(clean_settings)
    settings = get_parameters_from_general_settings(general_setting_dict)
    automl_settings_obj = AzureAutoMLSettings.from_string_or_dict(general_setting_dict)

    # JOS settings as a dictionary may or may not contain keys SDK uses during featurization and training
    # as a short term fix, the grain_column_names will be set here to ensure this setting is always
    # present in the settings passed to AutoML core SDK. As a long term fix we should figure out
    # how to use the automl_settings_obj which correctly sets all attributes, not matter what is sent by
    # JOS.
    settings[ForecastConstant.grain_column_names] = automl_settings_obj.grain_column_names
    return settings, automl_settings_obj, params['datasets.json']


def clean_general_settings_json_parse(orig_string: str) -> str:
    """Convert word/char into JSON parse form.

    :param orig_string: the original string to convert.
    :return:
    """
    ret_string = orig_string
    replace = {"None": "null", "True": "true", "False": "false", "'": "\""}
    for item in replace:
        ret_string = ret_string.replace(item, replace[item])
    return ret_string


def get_parameters_from_general_settings(general_setting_dict: dict) -> dict:
    """Collect parameter for training from setting.

    :param general_setting_dict: dictionary of parameters from automl settings.
    :return:
    """
    settings = {}
    if ForecastConstant.Horizon in general_setting_dict:
        if isinstance(general_setting_dict.get(ForecastConstant.Horizon, ForecastConstant.max_horizon_default), int):
            settings[ForecastConstant.Horizon] = int(general_setting_dict[ForecastConstant.Horizon])
        else:
            settings[ForecastConstant.Horizon] = ForecastConstant.auto
    if ForecastConstant.Lookback in general_setting_dict:
        settings[ForecastConstant.Lookback] = int(general_setting_dict[ForecastConstant.Lookback])
        settings[ForecastConstant.n_layers] = max(int(math.log2(settings[ForecastConstant.Lookback])), 1)
    if ForecastConstant.primary_metric in general_setting_dict:
        settings[ForecastConstant.primary_metric] = general_setting_dict.get(ForecastConstant.primary_metric,
                                                                             ForecastConstant.default_primary_metric)
    settings[ForecastConstant.CONSUME_DIST_FEATURIZATION_OUTPUT] = \
        general_setting_dict.get('forecasting_dnn_models_only') is True
    dataset_settings = {}
    for setting_name in ForecastConstant.FORECAST_VALID_SETTINGS:
        if setting_name in general_setting_dict:
            dataset_settings[setting_name] = general_setting_dict[setting_name]
    # This dataset settings dictionary is used as the ts_param_dict internally when the
    # TimeseriesDataset calls suggest_featurization_timeseries. To ensure the settings
    # are "valid" we must inject an empty grain column names here as well. Grain column
    # names might not be set by JOS when passed to the SDK at runtime. This object should
    # really use the same helper method as AutoML uses to create the ts_param_dict in the
    # short term. In the longer term we should consider using a strongly typed object which
    # requires or defaults all expected parameters.
    if ForecastConstant.grain_column_names not in dataset_settings:
        dataset_settings[ForecastConstant.grain_column_names] = None
    settings[ForecastConstant.dataset_settings] = dataset_settings
    return settings
