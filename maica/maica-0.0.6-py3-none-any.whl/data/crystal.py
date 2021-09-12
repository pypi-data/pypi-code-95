"""
Crystal Structure
-----------------
This module provides several utilities to handle the datasets of the crystsal structures.
Users can load the dataset of the crystal structures to ``GraphDataset`` object by calling ``load_dataset`` function.
"""


import numpy
from tqdm import tqdm
from maica.chem.base import load_elem_feats
from maica.data.base import read_data_file
from maica.data.util import impute
from maica.chem.crystal import even_samples
from maica.chem.crystal import get_crystal_graph
from maica.data.graph import GraphDataset


def load_dataset(path_dataset: str,
                 path_metadata_file: str,
                 idx_mid: numpy.ndarray,
                 idx_feat: numpy.ndarray,
                 idx_target: int,
                 impute_method: str = 'mean',
                 path_elem_embs: str = None):
    """
    Generate the ``GraphDataset`` object for a dataset of the crystal structures.
    It can be used for machine learning to predict materials properties from the crystal structures.

    :param path_dataset: (*str*) A path of the directory storing the CIF files.
    :param path_metadata_file: (*str*) A path of the metadata file of the dataset.
    :param idx_mid: (*numpy.ndarray*) Indices of the variables indicating the crystal structures in the dataset file.
    :param idx_feat: (*object*) Indices of the input numerical features in the data file.
    :param idx_target: (*object*) An index of the target variable in the data file.
    :param impute_method: (*str, optional*) A imputation method to fill empty data in the data file (default = ``maica.core.env.IMPUTE_KNN``).
    :param path_elem_embs: (*str, optional*) A path of JSON file storing user-defined elemental embeddings (*default* = ``None``).
    :return: A ``GraphDataset`` object.
    """

    elem_feats = load_elem_feats(path_elem_embs)
    rbf_means = even_samples(min_val=0, max_val=3, n_samples=64)
    metadata_file, metadata = read_data_file(path_metadata_file)
    dataset = list()
    idx_data = list()

    # Read numerical features.
    if idx_feat is not None:
        idx_feat = numpy.atleast_1d(idx_feat)
        metadata[:, idx_feat] = impute(metadata[:, idx_feat], impute_method)

    # Read crystal structures.
    idx_mid = numpy.atleast_1d(idx_mid)
    for i in tqdm(range(0, metadata.shape[0])):
        numeric_feats = None if idx_feat is None else metadata[i, idx_feat]
        targets = None if idx_target is None else metadata[i, idx_target]
        list_graphs = list()

        # If the data contains multiple crystal structures.
        for j in range(0, idx_mid.shape[0]):
            path_cif = path_dataset + '/' + str(metadata[i, idx_mid[j]]) + '.cif'
            mg = get_crystal_graph(elem_feats, path_cif, numeric_feats, rbf_means, targets, gid=i)

            if mg is not None:
                list_graphs.append(mg)

        if len(list_graphs) == idx_mid.shape[0]:
            dataset.append(list_graphs)
            idx_data.append(i)

    # Generate a graph dataset containing the crystal structures.
    dataset = GraphDataset(dataset, idx_mid, idx_feat, idx_target, metadata_file.columns, numpy.array(idx_data))

    return dataset
