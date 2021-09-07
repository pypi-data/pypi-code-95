# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains dataloader functions for the classification tasks."""

import logging
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from torch.utils.data import Dataset as PyTorchDataset
from typing import Tuple, Union, Optional

from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import (
    PyTorchDatasetWrapper,
    PyTorchMulticlassDatasetWrapper
)
from azureml.core import Dataset as AmlDataset
from azureml.core.workspace import Workspace


_logger = logging.getLogger(__name__)


def get_vectorizer(train_df: pd.DataFrame, val_df: Union[pd.DataFrame, None],
                   label_column_name: str) -> CountVectorizer:
    """Obtain labels vectorizer

    :param train_df: Training DataFrame
    :param val_df: Validation DataFrame
    :param label_column_name: Name/title of the label column
    :return: vectorizer
    """
    # Combine both dataframes if val_df exists
    if val_df is not None:
        combined_df = pd.concat([train_df, val_df])
    else:
        combined_df = train_df

    # Get combined label column
    combined_label_col = np.array(combined_df[label_column_name].astype(str))

    # TODO: CountVectorizer could run into memory issues for large datasets
    vectorizer = CountVectorizer(token_pattern=r"(?u)\b\w+\b", lowercase=False)
    vectorizer.fit(combined_label_col)

    return vectorizer


def multiclass_dataset_loader(
    dataset_id: str,
    validation_dataset_id: Union[str, None],
    label_column_name: str,
    workspace: Workspace,
    dataset_language: Optional[str] = 'eng'
) -> Tuple[PyTorchDataset,
           PyTorchDataset,
           np.ndarray,
           np.ndarray,
           Union[np.ndarray, None]]:
    """To get the training_set, validation_set and various label lists to generate metrics

    :param dataset_id: Unique identifier to fetch dataset from datastore
    :param validation_dataset_id: Unique identifier to fetch validation dataset from datastore
    :param label_column_name: Name/title of the label column
    :param workspace: workspace where dataset is stored in blob
    :param dataset_language: language code of dataset
    :return: training dataset, validation dataset, all class labels, train labels, y-validation
    """
    train_df, validation_df = _dataset_loader(dataset_id, validation_dataset_id, workspace)
    # Let's sort it for determinism
    train_label_list = np.array(sorted(pd.unique(train_df[label_column_name])))
    label_list = train_label_list
    validation_set = None
    y_val = None
    if validation_df is not None:
        y_val = np.array(validation_df[label_column_name])
        validation_df.drop(columns=label_column_name, inplace=True)
        val_label_list = pd.unique(y_val)
        label_list = np.array(sorted(set(train_label_list) | set(val_label_list)))
        validation_set = PyTorchMulticlassDatasetWrapper(validation_df, train_label_list,
                                                         dataset_language, label_column_name=None)
    training_set = PyTorchMulticlassDatasetWrapper(train_df, train_label_list,
                                                   dataset_language, label_column_name=label_column_name)
    return training_set, validation_set, label_list.astype(y_val.dtype), train_label_list.astype(y_val.dtype), y_val


def multilabel_dataset_loader(
    dataset_id: str,
    validation_dataset_id: Union[str, None],
    label_column_name: str,
    workspace: Workspace
) -> Tuple[PyTorchDataset,
           PyTorchDataset,
           int,
           CountVectorizer]:
    """To get the training_set, validation_set and num_label_columns for multilabel scenario

    :param dataset_id: Unique identifier to fetch dataset from datastore
    :param validation_dataset_id: Unique identifier to fetch validation dataset from datastore
    :param label_column_name: Name/title of the label column
    :param workspace: workspace where dataset is stored in blob
    :return: training dataset, validation dataset, num of label columns, vectorizer
    """
    train_df, validation_df = _dataset_loader(dataset_id, validation_dataset_id, workspace)
    # Fit a vectorizer on the label column so that we can transform labels column
    vectorizer = get_vectorizer(train_df, validation_df, label_column_name)
    num_label_cols = len(vectorizer.get_feature_names())

    # Convert dataset into the format ingestible be model
    _logger.info("TRAIN Dataset: {}".format(train_df.shape))
    training_set = PyTorchDatasetWrapper(train_df, label_column_name=label_column_name, vectorizer=vectorizer)
    validation_set = None
    if validation_df is not None:
        _logger.info("VALIDATION Dataset: {}".format(validation_df.shape))
        validation_set = PyTorchDatasetWrapper(validation_df,
                                               label_column_name=label_column_name,
                                               vectorizer=vectorizer)
    return training_set, validation_set, num_label_cols, vectorizer


def _dataset_loader(dataset_id: str,
                    validation_dataset_id: Union[str, None],
                    workspace: Workspace) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Get the train and val dataframes using the train and val dataset ids and the user's workspace

    :param dataset_id: Unique identifier to fetch dataset from datastore
    :param validation_dataset_id: Unique identifier to fetch validation dataset from datastore
    :param workspace: workspace where dataset is stored in blob
    :return: training dataframe, validation dataframe
    """
    # Get Training Dataset object and convert to pandas df
    train_ds = AmlDataset.get_by_id(workspace, dataset_id)
    _logger.info("Type of Dataset is: {}".format(type(train_ds)))
    train_df = train_ds.to_pandas_dataframe()

    # If validation dataset exists, get Validation Dataset object and convert to pandas df
    if validation_dataset_id is not None:
        validation_ds = AmlDataset.get_by_id(workspace, validation_dataset_id)
        _logger.info("Type of Validation Dataset is: {}".format(type(validation_ds)))
        validation_df = validation_ds.to_pandas_dataframe()
    else:
        validation_df = None
    return train_df, validation_df
