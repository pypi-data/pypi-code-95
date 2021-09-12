"""
Data Utilities
--------------
This module contains useful classes and functions for data pre-processing.
It can be used to convert user datasets into new dataset suitable for machine learning.
"""


import math
import numpy
from sklearn.impute import KNNImputer
from maica.core.env import *


def impute(data: numpy.ndarray,
           method: str):
    """
    Fill empty values in the given ``data``.
    It is useful for machine learning with the experimental data containing missing values.
    Three imputation methods are provided:

    - Mean-based imputation method.
    - Zero-based imputation method.
    - KNN-based imputation method.

    Possible values of ``method`` selecting the imputation method are given in ``maica.core.env``.

    :param data: (*numpy.ndarray*) Data object.
    :param method: (*str*) A key of the imputation method.
    :return: Data object.
    """

    if method == IMPUTE_MEAN:
        # Fill empty values by mean values.
        means = numpy.nanmean(data, axis=0)
        for i in range(0, data.shape[0]):
            for j in range(0, data.shape[1]):
                if math.isnan(float(data[i, j])):
                    data[i, j] = means[j]
    elif method == IMPUTE_ZERO:
        # Fill empty values by zero.
        for i in range(0, data.shape[0]):
            for j in range(0, data.shape[1]):
                if math.isnan(float(data[i, j])):
                    data[i, j] = 0
    elif method == IMPUTE_KNN:
        # Fill empty values using the values of k-nearest neighbor data.
        imputer = KNNImputer(n_neighbors=3)
        data = imputer.fit_transform(data)

    return data


def get_split_idx(n_data: int,
                  ratio: float):
    """
    Get indices that randomly split a set of {0, 1, ..., ``n_data``}.
    The set is divided into two subsets at a ratio of ``ratio`` to ``1 - ratio``.

    :param n_data: (*int*) The number of data in your data object.
    :param ratio: (*float*) The ratio for division.
    :return: Data indices of the two subsets.
    """

    if ratio >= 1 or ratio <= 0:
        raise AssertionError('Ratio must be in (0, 1), but the given ratio is {:.4f}'.format(ratio))

    n_dataset1 = int(ratio * n_data)
    idx_rand = numpy.random.permutation(n_data)

    return idx_rand[:n_dataset1], idx_rand[n_dataset1:]


def get_one_hot_feat(categories: list,
                     hot_category: object):
    """
    Generate one-hot encoding for the argument ``hot_category`` in the categories of ``categories``.

    :param categories: (*list*) A list of categories for the one-hot encoding.
    :param hot_category: (*object*) An emerged class in the one-hot encoding.
    :return: The one-hot encoding feature.
    """

    one_hot_feat = dict()

    for cat in categories:
        one_hot_feat[cat] = 0

    if hot_category in categories:
        one_hot_feat[hot_category] = 1

    return numpy.array(list(one_hot_feat.values()))
