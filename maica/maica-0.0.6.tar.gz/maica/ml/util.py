"""
Machine Learning Utilities
--------------------------
The ``maica.ml.util`` module provides essential functions for training configuration and model reuse.
Most deep learning algorithms in MAICA are based on this module.
"""

import numpy
import torch
import pandas
import os
import graphviz
import xgboost
import maica.ml.base
import maica.data.base
import torch.utils.data as tdata
import torch_geometric.data as tgdata
import maica.core.sys as sys
import maica.core.env as env
from sklearn.tree import export_graphviz
from maica.ml.base import SKLearnModel
from maica.ml.nn import FCNN
from maica.ml.nn import Autoencoder
from maica.ml.gnn import GCN
from maica.ml.gnn import GAT
from maica.ml.gnn import GIN
from maica.ml.gnn import CGCNN
from maica.data.base import Dataset
from maica.data.vector import VectorDataset
from maica.data.formula import FormDataset
from maica.data.graph import GraphDataset


class KFoldGenerator:
    def __init__(self,
                 dataset: Dataset,
                 k: int):
        self.sub_datasets = dataset.get_sub_datasets(k=k)

    def get(self,
            idx_fold: int):
        """
        Get training and test datasets for a given ``idx_fold``.

        :param idx_fold: (*int*) An index of the k-fold dataset.
        :return: Training and test datasets.
        """

        list_train_datasets = [self.sub_datasets[i] for i in range(0, len(self.sub_datasets)) if i != idx_fold]
        train_dataset = merge_datasets(list_train_datasets)
        test_dataset = self.sub_datasets[idx_fold]

        return train_dataset, test_dataset


def get_batch_sizes(n_data: int,
                    train_setting: int):
    """
    Return a batch size for stochastic gradient descent method according to the number of data and the train setting.

    :param n_data: (*int*) The number of data will be used to train.
    :param train_setting: (*int*) A hyperparameter determining the train settings.
    :return: A list of candidate batch sizes.
    """

    if n_data < 16:
        return [n_data]
    elif n_data < 32:
        return [16]
    elif n_data < 128:
        return [32]
    elif n_data < 256:
        return [64]
    else:
        # For data with a size >= 256.
        if train_setting == 0:
            return [64]
        elif train_setting == 1:
            return [64, 128]
        elif train_setting == 2:
            return [32, 64]
        elif train_setting == 3:
            return [32, 64, 128]
        elif train_setting == 4:
            return [32, 64, 128, 256]


def get_init_lrs(hparam_setting: int):
    """
    Return initial learning rates according to the given hyperparameter setting level.

    :param hparam_setting: (*int*) A hyperparameter determining the hyperparameter optimization of the model.
    :return: A list of candidate learning rates.
    """

    if hparam_setting == 0:
        return [1e-3]
    elif hparam_setting == 1:
        return [5e-3, 1e-3]
    elif hparam_setting == 2:
        return [5e-3, 1e-3, 5e-4]
    elif hparam_setting == 3:
        return [1e-2, 5e-3, 1e-3, 5e-4]
    elif hparam_setting == 4:
        return [5e-3, 1e-2, 5e-3, 1e-3, 5e-4, 1e-4]


def get_data_loader(*data: object,
                    batch_size: int = 8,
                    shuffle: bool = False):
    """
    Generate data loader object for a given dataset.
    If the given data is ``numpy.ndarray``, it returns ``torch.DataLoader`` object.
    If the data is ``maica.data.GraphDataset``, it returns ``torch_geometric.DataLoader`` object to iterate the graph-structured data.

    :param data: (*object*) The dataset to be iterated by the data loader.
    :param batch_size: (*int, optional*) The batch size of the data loader (*default* = 8).
    :param shuffle: (*int, optional*) An option to randomly sample the data when the iterations of the data loader (*default* = ``False``).
    :return: Data loader object of ``torch.DataLoader`` or ``torch_geometric.DataLoader``.
    """

    if isinstance(data[0], numpy.ndarray):
        # Generate data loader for the vector dataset including the numerical vectors and the chemical formulas.
        tensors = [torch.tensor(d, dtype=torch.float) for d in data]
        return tdata.DataLoader(tdata.TensorDataset(*tuple(tensors)), batch_size=batch_size, shuffle=shuffle)
    elif isinstance(data[0], GraphDataset):
        # Generate data loader for the graph dataset including the numerical vectors and the chemical formulas.
        return tgdata.DataLoader(data[0].data, batch_size=batch_size, shuffle=shuffle)
    else:
        raise AssertionError('The type of the given data object(s) is not valid.' +
                             ' Only numpy.ndarray and ml.data.Dataset is acceptable for this function.')


def get_optimizer(model_params: torch.Generator,
                  gd_name: str,
                  init_lr: float = 1e-3,
                  l2_reg: float = 1e-6):
    """
    Return a gradient descent optimizer to fit model parameters.

    :param model_params: (*torch.Generator*) Model parameters to be trained by the generated optimizer.
    :param gd_name: (*str*) A name of the gradient descent method to fit model parameters (defined in ``maica.core.env``).
    :param init_lr: (*float, optional*) An initial learning rate of the gradient descent optimizer.
    :param l2_reg: (*float, optional*) A coefficient of the L2 regularization in model parameters.
    :return: A gradient descent optimizer to fit model parameters.
    """

    # Define the gradient descent method to optimize the model parameters.
    if gd_name == env.GD_SGD:
        optimizer = torch.optim.SGD(model_params, lr=init_lr, weight_decay=l2_reg, momentum=0.9)
    elif gd_name == env.GD_ADADELTA:
        optimizer = torch.optim.Adadelta(model_params, lr=init_lr, weight_decay=l2_reg)
    elif gd_name == env.GD_RMSPROP:
        optimizer = torch.optim.RMSprop(model_params, lr=init_lr, weight_decay=l2_reg)
    elif gd_name == env.GD_ADAM:
        optimizer = torch.optim.Adam(model_params, lr=init_lr, weight_decay=l2_reg)
    else:
        raise AssertionError('Invalid request received with unknown name of the gradient method: {}.'.format(gd_name))

    return optimizer


def get_loss_func(loss_func: str):
    """
    Return a loss function to evaluate the model performance.

    :param loss_func: (*str*) A name of the loss function to evaluate model performance (defined in `maica.core.env``).
    :return: A loss function object to evaluate the model performance.
    """

    # Define the loss function to evaluate the model performance.
    if loss_func == env.LOSS_MAE:
        criterion = torch.nn.L1Loss()
    elif loss_func == env.LOSS_MSE:
        criterion = torch.nn.MSELoss()
    elif loss_func == env.LOSS_SMAE:
        criterion = torch.nn.SmoothL1Loss()
    else:
        raise AssertionError('Invalid request received with unknown name of the loss function: {}'.format(loss_func))

    return criterion


def get_model(alg_name: str,
              **kwargs):
    """
    Get a machine learning model for given algorithm name and model hyperparameters.
    The names of the algorithms are defined in ``maica.core.env``.

    :param alg_name: (*str*) A name of the machine learning algorithm (defined in ``maica.core.env``).
    :param kwargs: (*optional*) A dictionary containing model hyperparameters.
    :return: A machine learning model.
    """

    if alg_name in env.ALGS_SKLEARN:
        # Scikit-learn Algorithms
        return SKLearnModel(alg_name, **kwargs)
    elif alg_name in env.ALGS_PYTORCH:
        # Pytorch Algorithms
        if alg_name == env.ALG_FCNN:
            model = FCNN(dim_in=kwargs['dim_in'], dim_out=kwargs['dim_out'])
        elif alg_name == env.ALG_ATE:
            model = Autoencoder(dim_in=kwargs['dim_in'], dim_latent=kwargs['dim_latent'])
        elif alg_name == env.ALG_GCN:
            readout = kwargs['readout'] if 'readout' in kwargs.keys() else 'mean'
            n_graphs = kwargs['n_graphs'] if 'n_graphs' in kwargs.keys() else 1
            model = GCN(n_node_feats=kwargs['n_node_feats'], dim_out=kwargs['dim_out'], n_graphs=n_graphs,
                        readout=readout)
        elif alg_name == env.ALG_GAT:
            readout = kwargs['readout'] if 'readout' in kwargs.keys() else 'mean'
            n_graphs = kwargs['n_graphs'] if 'n_graphs' in kwargs.keys() else 1
            model = GAT(n_node_feats=kwargs['n_node_feats'], dim_out=kwargs['dim_out'], n_graphs=n_graphs,
                        readout=readout)
        elif alg_name == env.ALG_GIN:
            readout = kwargs['readout'] if 'readout' in kwargs.keys() else 'mean'
            n_graphs = kwargs['n_graphs'] if 'n_graphs' in kwargs.keys() else 1
            model = GIN(n_node_feats=kwargs['n_node_feats'], dim_out=kwargs['dim_out'], n_graphs=n_graphs,
                        readout=readout)
        elif alg_name == env.ALG_CGCNN:
            readout = kwargs['readout'] if 'readout' in kwargs.keys() else 'mean'
            n_graphs = kwargs['n_graphs'] if 'n_graphs' in kwargs.keys() else 1
            model = CGCNN(n_node_feats=kwargs['n_node_feats'], n_edge_feats=kwargs['n_edge_feats'],
                          dim_out=kwargs['dim_out'], n_graphs=n_graphs, readout=readout)
        else:
            raise AssertionError('Invalid request received with unknown algorithm name: {}.'.format(alg_name))

        # Move model parameters from CPU to GPU when sys.run_gpu is enabled.
        if sys.run_gpu:
            model.gpu()

        return model


def save_eval_results(task_name: str,
                      model: maica.ml.base.Model,
                      dataset_test: maica.data.base.Dataset,
                      preds: numpy.ndarray):
    """
    Save the model parameters and the prediction results as a model file and an excel file.

    :param task_name: (*str*) A name of your task.
    :param model: (*ml.base.Model)* A model used will be evaluated.
    :param dataset_test: (*data.base.Dataset*) A dataset used to the evaluation.
    :param preds: (*numpy.ndarray*) Prediction results of the model for the dataset.
    """

    # Make a directory to save the evaluation results.
    if not os.path.exists(task_name):
        os.mkdir(task_name)

    # Save the trained model.
    if model.alg_type == env.ALG_SKLEARN:
        model.save(task_name + '/model_' + model.alg_name + '.joblib')
    elif model.alg_type == env.ALG_PYTORCH:
        model.save(task_name + '/model_' + model.alg_name + '.pt')
    else:
        raise AssertionError('Unknown algorithm type: {}.'.format(model.alg_type))

    # Save the prediction results.
    idx_data = dataset_test.idx_data.reshape(-1, 1)
    targets = dataset_test.y.reshape(-1, 1)
    _preds = preds.reshape(-1, 1)
    df = pandas.DataFrame(numpy.hstack([idx_data, targets, _preds]))
    df.to_excel(task_name + '/pred_results_' + model.alg_name + '.xlsx',
                index=None, header=['data_index', 'target', 'prediction'])


def save_interpretation(model: maica.ml.base.Model,
                        file_name: str):
    """
    Save interpretable information of the machine learning algorithms.
    For non-interpretable algorithms, it raises ``AssertionError``.
    The following algorithms support this function.

    - Decision Tree Regression (ALG_DCTR).
    - Symbolic Regression (ALG_SYMR).
    - Gradient Boosting Tree Regression (ALG_GBTR).

    :param model: (*ml.base.Model*) A machine learning algorithm to generate interpretation about the prediction.
    :param file_name: (*str*) The path of file to store the generated interpretation.
    """

    if model.alg_name == env.ALG_DCTR:
        struct = export_graphviz(model.alg, feature_names=['feat #' + str(i) for i in range(0, model.alg.n_features_)])
        graphviz.Source(struct, format='png').render(file_name.replace('.png', ''), format='png')
    elif model.alg_name == env.ALG_SYMR:
        expression = model.alg._program.export_graphviz()
        graphviz.Source(expression, format='png').render(file_name.replace('.png', ''), format='png')
    elif model.alg_name == env.ALG_GBTR:
        xgboost.plot_importance(model.alg).figure.savefig(file_name)
    else:
        raise AssertionError('Interpretation is available for only the following algorithms.' +
                             '\n1. Decision Tree Regression.' +
                             '\n2. Symbolic Regression.' +
                             '\n3. Gradient Boosting Tree Regression.')


def merge_datasets(list_datasets: list):
    """
    Generate a dataset object from a list of datasets in ``list_datasets``.

    :param list_datasets: (*list*) A list of datasets.
    :return: Dataset object.
    """

    data = numpy.vstack([dataset.data for dataset in list_datasets])
    idx_data = numpy.hstack([dataset.idx_data for dataset in list_datasets])

    if isinstance(list_datasets[0], VectorDataset):
        dataset = VectorDataset(data, list_datasets[0].idx_feat, list_datasets[0].idx_target,
                                list_datasets[0].var_names, idx_data)
    elif isinstance(list_datasets[0], FormDataset):
        dataset = FormDataset(data, list_datasets[0].idx_form, list_datasets[0].idx_feat, list_datasets[0].idx_target,
                              list_datasets[0].var_names, idx_data)
    elif isinstance(list_datasets[0], GraphDataset):
        dataset = GraphDataset(data, list_datasets[0].idx_struct, list_datasets[0].idx_feat,
                               list_datasets[0].idx_target, list_datasets[0].var_names, idx_data)
    else:
        raise AssertionError('Unknown dataset type: {}.'.format(type(list_datasets[0])))

    return dataset
