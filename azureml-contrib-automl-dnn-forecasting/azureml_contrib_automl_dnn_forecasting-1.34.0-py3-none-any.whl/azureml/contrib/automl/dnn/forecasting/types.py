# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module containing Datatypes."""

from typing import Union

import azureml.dataprep as dprep
import numpy as np
import pandas as pd
from azureml.automl.runtime.featurizer.transformer.timeseries._distributed import DistributedTimeseriesTransformer
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer

DataInputType = Union[pd.DataFrame, dprep.Dataflow]
FeaturizerType = Union[DistributedTimeseriesTransformer, TimeSeriesTransformer]
TargetInputType = Union[DataInputType, np.ndarray, pd.Series]
