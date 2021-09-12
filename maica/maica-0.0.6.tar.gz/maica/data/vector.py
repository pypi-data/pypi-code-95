"""
Feature Vectors
---------------
This module provides a dataset class and data load function for the vector-shaped data.
It is useful in machine learning with the datasets such as feature vectors of compounds and engineering conditions.
If you want to handle the vector-shaped datasets, call ``load_dataset`` function in this module to load these datasets.
"""


import numpy
import torch
import copy
import maica.core.env
from sklearn.neighbors import LocalOutlierFactor
from maica.data.base import read_data_file
from maica.data.util import get_split_idx
from maica.data.util import impute
from maica.data.base import Dataset


class VectorDataset(Dataset):
    """
    A dataset object for vector-shaped data.
    It can contain all vector-shaped data regardless of the domain of the data.
    This class is useful to handle the numeric vectors, such as feature vectors of compounds and engineering conditions.
    """

    def __init__(self,
                 data: numpy.ndarray,
                 idx_feat: object,
                 idx_target: int,
                 var_names: numpy.ndarray,
                 idx_data: numpy.ndarray = None):
        """
        :param data: (*numpy.ndarray*) A ``numpy.ndarray`` object containing the actual data.
        :param idx_feat: (*object*) (*numpy.ndarray*) Indices of the numerical features in the dataset file.
        :param idx_target: (*int*) An index of the target value in the dataset file.
        :param var_names: (*numpy.ndarray*) (*numpy.ndarray*) Names of all variables in the dataset file.
        :param idx_data: (*numpy.ndarray*) Numerical indices of the data (*default* = ``None``).
        """

        # Feature and target information.
        self.idx_feat = copy.deepcopy(idx_feat)
        self.idx_target = idx_target
        self.contain_target = False if self.idx_target is None else True
        self.var_names = copy.deepcopy(var_names)
        self.feat_names = list()
        self.target_name = None if self.idx_target is None else self.var_names[idx_target]
        self.feat_types = list()

        # Data objects.
        self.data = copy.deepcopy(data)
        self.x = self.data[:, :-1] if self.contain_target else self.data
        self.y = self.data[:, -1].reshape(-1, 1) if self.contain_target else None
        self.n_data = self.data.shape[0]
        self.n_feats = self.x.shape[1]

        # Information of data indexing.
        self.idx_data = numpy.arange(0, self.data.shape[0]) if idx_data is None else copy.deepcopy(idx_data)

        # Tooltips for data visualization.
        self.tooltips = list()

        # Data statistics for normalization.
        self.feat_means = None
        self.feat_stds = None
        self.target_means = None
        self.target_stds = None

        # Initialize metadata of the dataset.
        if type(self).__name__ == 'VectorDataset':
            self._set_feat_names()
            self._set_tooltips()

    def _set_feat_names(self):
        """
        Set names and types of the input features.
        """

        for idx in self.idx_feat:
            self.feat_names.append(self.var_names[idx])
            self.feat_types.append('num')

    def _set_tooltips(self):
        """
        Set tooltip for each data to identify it in the data visualization.
        """

        for i in range(0, self.data.shape[0]):
            self.tooltips.append('Data idx: ' + str(self.idx_data[i]))

    def normalize(self):
        """
        Normalize the input data based on the z-score.
        For vector-shaped data :math:`\mathbf{x}`, the z-score is defined by:

        .. math::
            \mathbf{z} = \\frac{\mathbf{x} - \mathbf{\mu}}{\mathbf{\sigma}},

        where :math:`\mathbf{\mu}` is the mean of the data, and :math:`\mathbf{\sigma}` is the standard deviation of the data.
        Note that all mathematical operations are applied dimensional-wise.
        """

        if self.contain_target:
            # For a dataset containing the target properties.
            self.feat_means = numpy.mean(self.data[:, :-1], axis=0)
            self.feat_stds = numpy.std(self.data[:, :-1], axis=0) + 1e-6
            self.data[:, :-1] = (self.data[:, :-1] - self.feat_means) / self.feat_stds
        else:
            # For a dataset without the target properties.
            self.feat_means = numpy.mean(self.data, axis=0)
            self.feat_stds = numpy.std(self.data, axis=0) + 1e-6
            self.data = (self.data - self.feat_means) / self.feat_stds

    def denormalize(self):
        """
        Restore the normalize input data.
        For vector-shaped normalized data :math:`\mathbf{z}`, the denormalized (oroginal) data is calculated by:

        .. math::
            \mathbf{x} = \mathbf{\sigma} \mathbf{z} + \mathbf{\mu},

        where :math:`\mathbf{\mu}` is the mean of the data, and :math:`\mathbf{\sigma}` is the standard deviation of the data.
        Note that all mathematical operations are applied dimensional-wise.
        """

        if self.feat_means is None:
            raise AssertionError('The input data of this dataset has never been normalized.')

        if self.contain_target:
            # For a dataset containing the target properties.
            self.data[:, :-1] = self.feat_stds * self.data[:, :-1] + self.feat_means
        else:
            # For a dataset without the target properties.
            self.data = self.feat_stds * self.data + self.feat_means

    def normalize_target(self):
        """
        Normalize the target values based on the z-score.
        For a target value :math:`y`, the z-score is defined by:

        .. math::
            z = \\frac{y - \mu}{\sigma},

        where :math:`\mu` is the mean of the target values, and :math:`\mathbf{\sigma}` is the standard deviation of the target values.
        Note that all mathematical operations are applied dimensional-wise.
        """

        if not self.contain_target:
            raise AssertionError('This dataset does not contain the target values.')

        self.target_means = numpy.mean(self.data[:, -1], axis=0)
        self.target_stds = numpy.std(self.data[:, -1], axis=0) + 1e-6
        self.data[:, -1] = (self.data[:, -1] - self.target_means) / self.target_stds

    def denormalize_target(self):
        """
        Restore the normalize target values.
        For a normalized target value :math:`z`, the denormalized (oroginal) target value is calculated by:

        .. math::
            y = \sigma z + \mu,

        where :math:`\mu` is the mean of the target values, and :math:`\sigma` is the standard deviation of the target values.
        Note that all mathematical operations are applied dimensional-wise.
        """

        if self.target_means is None:
            raise AssertionError('The target values of this dataset has never been normalized.')

        self.data[:, -1] = self.target_stds * self.data[:, -1] + self.target_means

    def to_tensor(self):
        """
        Convert the data objects of numpy.ndarray into the data objects of torch.Tensor.
        """

        self.data = torch.tensor(self.data, dtype=torch.float)
        self.x = self.data[:, :-1] if self.contain_target else self.data
        self.y = self.data[:, -1].reshape(-1, 1) if self.contain_target else None

    def remove_outliers(self):
        """
        Remove outliers in the dataset using Local Outlier Factor (LOF).
        """

        # Remove outliers using local outlier factor (LOF).
        lof = LocalOutlierFactor(n_neighbors=int(numpy.sqrt(self.data.shape[0])))
        ind = lof.fit_predict(self.x())
        self.data = self.data[ind == 1, :]

        # Replace tooltips of the data.
        self.tooltips = [self.tooltips[i] for i in range(0, len(self.data)) if ind[i] == 1]

    def split(self,
              ratio: float):
        """
        Split the dataset into two sub-datasets based on the given ratio.
        Two sub-datasets and the original indices of the data in them are returned.

        :param ratio: (*float*) Ratio between two sub-datasets. The sub-datasets are dived by a ratio of ``ratio`` to ``1 - ratio``.
        :return: Two sub-datasets.
        """

        # Randomly sample the dataset.
        idx_dataset1, idx_dataset2 = get_split_idx(self.data.shape[0], ratio)

        # Split dataset into the two subsets.
        dataset1 = VectorDataset(self.data[idx_dataset1, :], self.idx_feat, self.idx_target, self.var_names,
                                 self.idx_data[idx_dataset1])
        dataset2 = VectorDataset(self.data[idx_dataset2, :], self.idx_feat, self.idx_target, self.var_names,
                                 self.idx_data[idx_dataset2])

        return dataset1, dataset2

    def get_sub_datasets(self,
                         k: int):
        """
        Split the dataset into the :math:`k` sub-datasets without repeating the data.
        In the training, :math:`k-1` sub-datasets are used to train the model, and the remaining sub-dataset is used for evaluation.

        :param k: (*int*) The number of subsets.
        :return: A list of :math:`k` sub-datasets.
        """

        idx_rand = numpy.random.permutation(self.n_data)
        n_data_subset = int(self.n_data / k)
        sub_datasets = list()

        # Get k-1 sub-datasets with the same size.
        for i in range(0, k-1):
            idx_sub_dataset = idx_rand[i*n_data_subset:(i+1)*n_data_subset]
            sub_dataset = VectorDataset(self.data[idx_sub_dataset, :], self.idx_feat, self.idx_target,
                                        self.var_names, self.idx_data[idx_sub_dataset])
            sub_datasets.append(sub_dataset)

        # Get the last sub-dataset containing the all remaining data.
        idx_sub_dataset = idx_rand[(k-1)*n_data_subset:]
        sub_dataset = VectorDataset(self.data[idx_sub_dataset, :], self.idx_feat, self.idx_target,
                                    self.var_names, self.idx_data[idx_sub_dataset])
        sub_datasets.append(sub_dataset)

        return sub_datasets


def load_dataset(path_data_file: str,
                 idx_feat: object,
                 idx_target: int,
                 impute_method: str = maica.core.env.IMPUTE_KNN):
    """
    Load a vector-shaped dataset to the ``maica.data.vector.VectorDataset`` object.

    :param path_data_file: (*str*) The path of the data file.
    :param idx_feat: (*object*) Indices of the input features in the data file.
    :param idx_target: (*int*) An index of the target variable in the data file.
    :param impute_method: (*str, optional*) A imputation method to fill empty data in the data file (*default* = ``maica.core.env.IMPUTE_KNN``).
    :return: A ``VectorDataset`` object containing the dataset.
    """

    data_file, data_obj = read_data_file(path_data_file)
    var_names = data_file.columns.values
    data = list()

    # Read input data.
    idx_feat = numpy.atleast_1d(idx_feat)
    data.append(impute(data_obj[:, idx_feat], impute_method))

    # Read target data.
    if idx_target is not None:
        data.append(data_obj[:, idx_target].reshape(-1, 1))

    # Generate a vector dataset containing feature vectors.
    dataset = numpy.hstack(data).astype(numpy.float)

    return VectorDataset(dataset, idx_feat, idx_target, var_names)
