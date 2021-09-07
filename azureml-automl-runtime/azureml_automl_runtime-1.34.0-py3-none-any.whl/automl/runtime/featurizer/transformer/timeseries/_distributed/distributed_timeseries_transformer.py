# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import numpy as np
import pandas as pd
from azureml.automl.runtime.featurizer.transformer.timeseries._distributed import distributed_timeseries_util


class DistributedTimeseriesTransformer:

    def __init__(self, grain_col_names):
        self._grain_col_names = grain_col_names
        self._grains_to_transformers = {}

    @property
    def transformers(self):
        return list(self._grains_to_transformers.values())

    def add_transformer_for_grain(self, grain_dict, transformer):
        grain_dict_str = distributed_timeseries_util.convert_grain_dict_to_str(grain_dict)
        self._grains_to_transformers[grain_dict_str] = transformer

    def transform(self, X, y):
        if isinstance(y, np.ndarray):
            y = pd.DataFrame(y)
        data = pd.concat([X, y], axis=1)
        groupby = data.groupby(self._grain_col_names)
        transformed_dfs = []
        for grain in groupby.groups:
            grain_dict = {self._grain_col_names[i]: grain[i] for i in range(len(self._grain_col_names))}
            transform = self._grains_to_transformers[
                distributed_timeseries_util.convert_grain_dict_to_str(grain_dict)]
            df = groupby.get_group(grain)
            if y is None:
                X_df, y_df = df, None
            else:
                X_df, y_df = df.iloc[:, :-1].reset_index(drop=True), df.iloc[:, -1].values
            transformed_df = transform.transform(X_df, y_df)
            transformed_dfs.append(transformed_df)
        return pd.concat(transformed_dfs)
