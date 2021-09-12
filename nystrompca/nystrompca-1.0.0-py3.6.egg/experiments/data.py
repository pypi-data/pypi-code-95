
# Copyright 2020 Fredrik Hallgren
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
This module contains function to read different datasets from the
UCI machine learning repository. The raw dataset are included in
the repository in the `data/` folder in the root directory.

"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import load_digits


DATA_FOLDER = Path(__file__).parent.joinpath('../../data/')


def get_magic_data(n: int) -> np.ndarray:
    """
    Read the magic telescope data

    Parameters
    ----------
    n : int
        Maximum number of data points

    Returns
    -------
    data : numpy.ndarray
        Data matrix

    """
    data = []
    with open(DATA_FOLDER.joinpath("magic_gamma_telescope.dat")) as f:
        for line in f.readlines():
            split_line = line.split(',')[:-1]
            data.append(split_line)

    data = np.asarray(data, dtype=np.float64)

    data = data[:n]

    return data


def get_yeast_data(n: int) -> np.ndarray:
    """
    Read the yeast dataset with protein location sites for fungi

    Parameters
    ----------
    n : int
        Maximum number of data points

    Returns
    -------
    data : numpy.ndarray
        Data matrix

    """
    df = pd.read_csv(DATA_FOLDER.joinpath("yeast.dat"), header=None,
                     delimiter='\s+')

    df.drop(0, axis=1, inplace=True)

    df = pd.get_dummies(df)

    return df.values[:n]


def get_cardiotocography_data(n: int) -> np.ndarray:
    """
    Read the cardiotocography dataset with heart measurement data

    Parameters
    ----------
    n : int
        Maximum number of data points

    Returns
    -------
    data : numpy.ndarray
        Data matrix

    """
    data = []
    with open(DATA_FOLDER.joinpath("cardiotocography.dat")) as f:
        for line in f.readlines():
            line = line.split('\n')[0]
            split_line = line.split('\t')[3:] # keep numeric data
            data.append(split_line)

    data = np.asarray(data, dtype=np.float64)

    data = data[:n]

    return data


def get_segmentation_data(n: int) -> np.ndarray:
    """
    Read the segmentation dataset with various data on images

    Parameters
    ----------
    n : int
        Maximum number of data points

    Returns
    -------
    data : numpy.ndarray
        Data matrix

    """
    data = []
    with open(DATA_FOLDER.joinpath("segmentation.dat")) as f:
        for line in f.readlines():
            split_line = line.split(' ')
            data.append(split_line)

    data = np.asarray(data, dtype=np.float64)

    data = data[:n]

    return data


def get_digits_data(n: int) -> np.ndarray:
    """
    Read the digits dataset from UCI through the scikit-learn helper
    function. The dataset contains the flattened grayscale pixel values
    from 8x8 images of handwritten digits.

    Parameters
    ----------
    n : int
        Maximum number of data points

    Returns
    -------
    X : numpy.ndarray, 2d
        Independent variables

    """
    digits = load_digits()

    return digits['data']


def get_dailykos_data(n: int) -> np.ndarray:
    """
    """
    df = read_bag_of_words('dailykos.dat')

    return df.values[:n]


def get_nips_data(n: int) -> np.ndarray:
    """
    """
    df = read_bag_of_words('nips.dat')

    return df.values[:n]


def read_bag_of_words(dataset: str) -> pd.DataFrame:

    df = pd.read_csv(DATA_FOLDER.joinpath(dataset),
                     names=['docID','wordID','count'], delimiter=' ')

    df = df.pivot(index='docID', columns='wordID', values='count')

    df.replace(to_replace=np.nan, value=0, inplace=True)

    return df


def get_facebook_data(n: int) -> np.ndarray:
    """
    """
    df = pd.read_csv(DATA_FOLDER.joinpath('facebook.dat'),
                     names=['node1', 'node2'])

    df['edge'] = 1

    df = df.pivot(index='node1', columns='node2', values='edge')

    df.replace(to_replace=np.nan, value=0, inplace=True)

    first_idxs = list(set(df.index) & set(df.columns))[:n]

    df = df.loc[first_idxs, first_idxs]

    return df.values


def get_airfoil_data(n: int) -> (np.ndarray, np.ndarray):
    """
    Read the airfoil dataset with wind tunnel measurements from NASA.
    This dataset is used in the regression experiments.

    Parameters
    ----------
    n : int
        Maximum number of data points

    Returns
    -------
    X : numpy.ndarray, 2d
        Independent variables
    y : numpy.ndarray, 1d
        Dependent variable

    """
    data = []
    with open(DATA_FOLDER.joinpath("airfoil.dat")) as f:
        for line in f.readlines():
            split_line = line.split('\t')
            data.append(split_line)

    data = np.asarray(data, dtype=np.float64)

    data = data[:n]

    X = data[:,:-1]
    y = data[:,-1]

    return X, y

