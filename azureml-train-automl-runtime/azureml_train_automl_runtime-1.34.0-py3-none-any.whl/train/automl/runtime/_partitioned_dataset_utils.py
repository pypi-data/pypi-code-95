# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import random
from typing import Dict, Any

import dask.dataframe as dd
import dask.delayed as ddelayed
from azureml.data import TabularDataset


def _get_dataset_for_grain(grain_keys_values: Dict[str, Any],
                           partitioned_dataset: TabularDataset) -> TabularDataset:
    filter_condition = None
    for key, value in grain_keys_values.items():
        new_condition = partitioned_dataset[key] == value
        filter_condition = new_condition if filter_condition is None else filter_condition & new_condition
    return partitioned_dataset.filter(filter_condition)


def _to_partitioned_dask_dataframe(partitioned_dataset: TabularDataset) -> dd:
    datasets_for_all_grains = [_get_dataset_for_grain(kv, partitioned_dataset)
                               for kv in partitioned_dataset.get_partition_key_values()]
    delayed_functions = [ddelayed(dataset_for_grain.to_pandas_dataframe)()
                         for dataset_for_grain in datasets_for_all_grains]
    ddf = dd.from_delayed(delayed_functions)
    return ddf


def _to_dask_dataframe_of_random_grains(partitioned_dataset: TabularDataset, grain_count: int) -> dd:
    partition_key_values = partitioned_dataset.get_partition_key_values()
    if grain_count < len(partition_key_values):
        partition_key_values = random.sample(partition_key_values, grain_count)

    datasets_for_all_grains = [_get_dataset_for_grain(kv, partitioned_dataset)
                               for kv in partition_key_values]
    delayed_functions = [ddelayed(dataset_for_grain.to_pandas_dataframe)()
                         for dataset_for_grain in datasets_for_all_grains]
    ddf = dd.from_delayed(delayed_functions)
    return ddf
