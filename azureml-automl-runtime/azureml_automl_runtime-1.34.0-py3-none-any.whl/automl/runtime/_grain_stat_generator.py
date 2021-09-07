# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, Dict, Any, Tuple

import pandas as pd
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.data import TabularDataset
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings

from azureml.automl.runtime.frequency_fixer \
    import COVERAGE, improved_infer_freq_one_grain, FREQUENCY_REJECT_TOLERANCE, FREQ, START, str_to_offset_safe
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame


class GrainStatistics:
    """
    All stats for one grain should be included in this class as simple data members
    This should include no business logic
    """

    def __init__(
        self,
        grain_keys_values: Dict[str, Any],
        frequency: Optional[pd.DateOffset],
        start_time: pd.Timestamp,
        end_time: pd.Timestamp,
        total_rows: int,
        total_rows_in_coverage: int
    ):
        self.grain_keys_values = grain_keys_values
        self.frequency = frequency
        self.start_time = start_time
        self.end = end_time
        self.total_rows = total_rows
        self.total_rows_in_coverage = total_rows_in_coverage


def _get_grain_stat(
    dataset_for_grain: TabularDataset,
    grain_keys_values: Dict[str, Any],
    automl_settings: AzureAutoMLSettings
) -> GrainStatistics:
    X = dataset_for_grain.to_pandas_dataframe()

    user_freq = str_to_offset_safe(automl_settings.freq, ReferenceCodes._STAT_GENERATOR_FREQ_FIX)
    aggregation_enabled = automl_settings.target_aggregation_function is not None and automl_settings.freq is not None

    tsdf = TimeSeriesDataFrame(
        X,
        time_colname=automl_settings.time_column_name,
        grain_colnames=automl_settings.grain_column_names,
        ts_value_colname=automl_settings.label_column_name
    )

    frequency, start, points_covered = _get_grain_frequency_and_start(
        tsdf,
        grain_keys_values,
        None if aggregation_enabled else user_freq
    )
    return GrainStatistics(grain_keys_values, frequency, start, tsdf.time_index.max(), X.shape[0], points_covered)


def _get_grain_frequency_and_start(
    tsdf: TimeSeriesDataFrame,
    grain_keys_values: Dict[str, Any],
    user_frequency:
    Optional[pd.DateOffset] = None
) -> Tuple[Optional[pd.DateOffset], pd.Timestamp, int]:
    tsdf.sort_index(inplace=True)
    freq_offset = tsdf.infer_freq(return_freq_string=False)
    series_data = improved_infer_freq_one_grain(
        tsdf, freq_offset, list(grain_keys_values.values()), user_frequency, FREQUENCY_REJECT_TOLERANCE)
    return series_data[FREQ], series_data[START], series_data[COVERAGE]
