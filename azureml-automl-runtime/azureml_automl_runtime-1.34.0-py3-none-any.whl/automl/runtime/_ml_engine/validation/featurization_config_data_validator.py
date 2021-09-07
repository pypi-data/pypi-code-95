# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional

import logging
import pandas as pd

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.constants import FeatureType, SupportedTransformers, TransformerParams
from azureml.automl.core.shared.constants import TimeSeriesInternal
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    InvalidInputDatatypeFeaturizatonConfig,
    MissingColumnsInData
)
from azureml.automl.runtime._ml_engine.validation.validators import AbstractRawExperimentDataValidator
from azureml.automl.runtime.column_purpose_detection import ColumnPurposeSweeper
from azureml.automl.runtime._data_definition import RawExperimentData
from azureml.automl.runtime.shared import utilities as runtime_utilities


logger = logging.getLogger(__name__)


class FeaturizationConfigDataValidator(AbstractRawExperimentDataValidator):
    """
    Class for featurizationConfig and input data validation.
    """

    def __init__(self, featurization_config: FeaturizationConfig, is_timeseries: bool):
        """
        Initialization for FeaturizationConfigDataValidator.

        :param featurization_config: The featurization config that needs validation.
        :param is_timeseries: Is timeseries task or not.
        """
        super(FeaturizationConfigDataValidator, self).__init__()
        self._featurization_config = featurization_config
        self._is_timeseries = is_timeseries

    def validate_raw_experiment_data(self, data: RawExperimentData) -> None:
        """
        Validate the input data with the featurization config.

        :param data: The data needs to be validated.
        """
        if data.X is None:
            return

        self._validate_imputer_data(data)
        self._validate_column_purpose_data(data)

    def _validate_imputer_data(self, data: RawExperimentData) -> None:
        """Validate imputer related data."""
        if not self._featurization_config.transformer_params:
            return

        for transformer, transformer_params_list in self._featurization_config.transformer_params.items():
            for cols, params in transformer_params_list:
                for col in cols:
                    self._validate_col_in_data(col, data.X, SupportedTransformers.Imputer, data.target_column_name)
                    if transformer == SupportedTransformers.Imputer:
                        self._validate_numerical_imputer_data_type(
                            params.get(TransformerParams.Imputer.Strategy), data.X, col
                        )

    def _validate_column_purpose_data(self, data: RawExperimentData) -> None:
        """Validate Column purpose data."""
        if not self._featurization_config.column_purposes:
            return
        for col, purpose in self._featurization_config.column_purposes.items():
            self._validate_col_in_data(col, data.X, "column purpose")
            self._validate_data_type(data.X, col, "column purposes {}".format(purpose), purpose)

    def _validate_col_in_data(
            self,
            col: str,
            df: pd.DataFrame,
            config_name: str,
            target_column_name: Optional[str] = None
    ) -> None:
        """Validate column in data."""
        if self._is_timeseries and (col == target_column_name or col == TimeSeriesInternal.DUMMY_TARGET_COLUMN) \
                and config_name == SupportedTransformers.Imputer:
            return
        if col not in df.columns:
            raise DataException._with_error(AzureMLError.create(
                MissingColumnsInData, target="featurization_config",
                columns="{} in featurization config's {}".format(col, config_name),
                data_object_name="X",
                reference_code=ReferenceCodes._FEATURIZATION_CONFIG_MISSING_COLUMN)
            )

    def _validate_numerical_imputer_data_type(
            self,
            strategy: Optional[str],
            df: pd.DataFrame,
            col: str
    ) -> None:
        """Validate the data type of the imputer."""
        if strategy is None:
            return
        if strategy in TransformerParams.Imputer.NumericalImputerStrategies:
            self._validate_data_type(
                df, col, "imputer with strategy {}".format(strategy), FeatureType.Numeric
            )

    def _validate_data_type(
            self,
            df: pd.DataFrame,
            col: str,
            featurization_option: str,
            expected_type: str
    ) -> None:
        """Validate the data to be expected type."""
        if col not in df.columns:
            return
        inferred_dtype = runtime_utilities._get_column_data_type_as_str(df[col].values)
        type_convert_dict = {FeatureType.Numeric: 'np.float', FeatureType.DateTime: 'np.datetime64'}
        if not ColumnPurposeSweeper.is_feature_type_convertible(expected_type, inferred_dtype):
            raise DataException._with_error(AzureMLError.create(
                InvalidInputDatatypeFeaturizatonConfig, target="featurization_config", column_name=col,
                data_type=type_convert_dict.get(expected_type), featurization_option=featurization_option,
                reference_code=ReferenceCodes._FEATURIZATION_CONFIG_INVALID_DATA_TYPE)
            )

        if self._is_timeseries:
            # for forecasting tasks it need to fail the run if the actual conversion is failed.
            try:
                if expected_type == FeatureType.DateTime:
                    pd.to_datetime(df[col])
            except (ValueError, TypeError) as e:
                raise DataException._with_error(AzureMLError.create(
                    InvalidInputDatatypeFeaturizatonConfig, target="featurization_config", column_name=col,
                    data_type=type_convert_dict.get(expected_type), featurization_option=featurization_option,
                    reference_code=ReferenceCodes._FEATURIZATION_CONFIG_INVALID_DATA_TYPE_TIMESERIES),
                    inner_exception=e
                ) from e
