"""
Transfer Learning
-----------------
This module includes several functions to perform transfer learning using neural networks.
Popular transfer learning methods called :obj:`retrain head` and :obj:`fine tuning` are provided as built-in functions.
"""

import numpy
import torch
import maica.ml.base
import maica.data.base
import maica.core.env as env
import maica.ml.util as mu
from maica.data.vector import VectorDataset
from maica.data.graph import GraphDataset


def tl_retrain_head(path_source_model,
                    model_target: maica.ml.base.Model,
                    dataset_target: maica.data.base.Dataset,
                    gd_name: str = env.GD_ADAM,
                    init_lr: float = 1e-3,
                    l2_reg: float = 1e-6,
                    loss_func: str = env.LOSS_MAE,
                    max_epoch: int = 300):
    """
    Perform transfer learning based on feature extractor of the source model.
    The feature extraction layers of the source model are frozen in the training on the target dataset.
    Only the prediction layer called head is trained during the training on the target dataset.
    This transfer learning method is called 'retrain head'.

    :param path_source_model: (str) The path of the model file of the source model.
    :param model_target: (ml.base.Model) Target model that will be used for transfer learning.
    :param dataset_target: (data.base.Dataset) Target dataset for transfer learning.
    :param gd_name: (str, optional) A name of the optimizer to train the target model (default = AdamOptimizer)
    :param init_lr: (float, optional) An initial learning rate of the gradient descent optimizer (default = 1e-3).
    :param l2_reg: (float, optional) A coefficient of the L2 regularization in model parameters (Default = 1e-6).
    :param loss_func: (str, optional) A name of loss function to evaluate the model performance (default = Mean Absolute Error).
    :param max_epoch: (int, optional) The maximum iteration of the model parameter optimization in the training.
    :return: Trained model.
    """

    # Load model parameters of the source model into the target model.
    model_target.load(path_source_model)

    # Randomly initialize the model parameters of the last layer.
    head = list(model_target.children())[-1]
    torch.nn.init.normal_(head.weight)
    if head.bias is not None:
        torch.nn.init.normal_(head.bias)

    # Generate data loader of the target dataset.
    batch_size = int(numpy.minimum(64, dataset_target.n_data()))
    if isinstance(dataset_target, VectorDataset):
        data_loader = mu.get_data_loader(dataset_target.x(), dataset_target.y(), batch_size=batch_size, shuffle=True)
    elif isinstance(dataset_target, GraphDataset):
        data_loader = mu.get_data_loader(dataset_target, batch_size=batch_size, shuffle=True)

    # Get optimizer and loss function for the training.
    optimizer = mu.get_optimizer(head.parameters(), gd_name=gd_name, init_lr=init_lr, l2_reg=l2_reg)
    loss_func = mu.get_loss_func(loss_func=loss_func)

    # Optimize model parameters of the neural network.
    for i in range(0, max_epoch):
        train_loss = model_target.fit(data_loader, optimizer, loss_func)
        print('Epoch [{}/{}]\tTrain loss: {:.4f}'.format(i + 1, max_epoch, train_loss))

    return model_target


def tl_fine_tuning(path_source_model,
                   model_target: maica.ml.base.Model,
                   dataset_target: maica.data.base.Dataset,
                   gd_name: str = env.GD_ADAM,
                   init_lr: float = 1e-6,
                   l2_reg: float = 1e-6,
                   loss_func: str = env.LOSS_MAE,
                   max_epoch: int = 300):
    """
    Perform transfer learning based on a pre-trained source model.
    The target model is initialized by the model parameters of the source model.
    After the initialization, the target model is trained on the target dataset with a small learning rate.
    This transfer learning method is called 'fine tuning'.

    :param path_source_model: (str) The path of the model file of the source model.
    :param model_target: (ml.base.Model) Target model that will be used for transfer learning.
    :param dataset_target: (data.base.Dataset) Target dataset for transfer learning.
    :param gd_name: (str, optional) A name of the optimizer to train the target model (default = AdamOptimizer)
    :param init_lr: (float, optional) An initial learning rate of the gradient descent optimizer (default = 1e-3).
    :param l2_reg: (float, optional) A coefficient of the L2 regularization in model parameters (Default = 1e-6).
    :param loss_func: (str, optional) A name of loss function to evaluate the model performance (default = Mean Absolute Error).
    :param max_epoch: (int, optional) The maximum iteration of the model parameter optimization in the training.
    :return: Trained model.
    """

    # Load model parameters of the source model into the target model.
    model_target.load(path_source_model)

    # Generate data loader of the target dataset.
    batch_size = int(numpy.minimum(64, dataset_target.n_data()))
    if isinstance(dataset_target, VectorDataset):
        data_loader = mu.get_data_loader(dataset_target.x(), dataset_target.y(), batch_size=batch_size, shuffle=True)
    elif isinstance(dataset_target, GraphDataset):
        data_loader = mu.get_data_loader(dataset_target, batch_size=batch_size, shuffle=True)

    # Get optimizer and loss function for the training.
    optimizer = mu.get_optimizer(model_target.parameters(), gd_name=gd_name, init_lr=init_lr, l2_reg=l2_reg)
    loss_func = mu.get_loss_func(loss_func=loss_func)

    # Optimize model parameters of the neural network.
    for i in range(0, max_epoch):
        train_loss = model_target.fit(data_loader, optimizer, loss_func)
        print('Epoch [{}/{}]\tTrain loss: {:.4f}'.format(i + 1, max_epoch, train_loss))

    return model_target
