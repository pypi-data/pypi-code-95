from enum import Enum

import torch.nn as nn
import torch.nn.init as init
from torch.optim.lr_scheduler import LambdaLR


def set_seed(seed_val: int, os_, random_, numpy_, torch_):
    """Set random seed for build-in and external modules.

    set global random seed for reproducibility for os, random, numpy and torch.

    Args:
        seed_val (int): random seed value
        os_ (module): os 
        random_ (module): random
        numpy_ (module): numpy
        torch_ (module): torch

    Usage:
        >>> import os
        >>> import torch
        >>> import random
        >>> import numpy as np

        >>> os, random, np, torch = set_seed(0, os, random, np, torch)
    """
    # 1. Set `PYTHONHASHSEED` environment variable at a fixed value
    os_.environ['PYTHONHASHSEED'] = str(seed_val)

    # 2. Set `python` built-in pseudo-random generator at a fixed value
    random_.seed(seed_val)

    # 3. Set `numpy` pseudo-random generator at a fixed value
    numpy_.random.seed(seed_val)

    # 4. Set `pytorch` pseudo-random generator at a fixed value
    torch_.manual_seed(seed_val)

    return os_, random_, numpy_, torch_


def weight_init(m):
    """Init weight for torch modules.

    Usage:
        model = Model()
        model.apply(weight_init)
    """
    if isinstance(m, nn.Conv1d):
        init.normal_(m.weight.data)
        if m.bias is not None:
            init.normal_(m.bias.data)
    elif isinstance(m, nn.Conv2d):
        init.xavier_normal_(m.weight.data)
        if m.bias is not None:
            init.normal_(m.bias.data)
    elif isinstance(m, nn.Conv3d):
        init.xavier_normal_(m.weight.data)
        if m.bias is not None:
            init.normal_(m.bias.data)
    elif isinstance(m, nn.ConvTranspose1d):
        init.normal_(m.weight.data)
        if m.bias is not None:
            init.normal_(m.bias.data)
    elif isinstance(m, nn.ConvTranspose2d):
        init.xavier_normal_(m.weight.data)
        if m.bias is not None:
            init.normal_(m.bias.data)
    elif isinstance(m, nn.ConvTranspose3d):
        init.xavier_normal_(m.weight.data)
        if m.bias is not None:
            init.normal_(m.bias.data)
    elif isinstance(m, nn.BatchNorm1d):
        init.normal_(m.weight.data, mean=1, std=0.02)
        init.constant_(m.bias.data, 0)
    elif isinstance(m, nn.BatchNorm2d):
        init.normal_(m.weight.data, mean=1, std=0.02)
        init.constant_(m.bias.data, 0)
    elif isinstance(m, nn.BatchNorm3d):
        init.normal_(m.weight.data, mean=1, std=0.02)
        init.constant_(m.bias.data, 0)
    elif isinstance(m, nn.Linear):
        init.xavier_normal_(m.weight.data)
        if m.bias is not None:
            init.normal_(m.bias.data)
    elif isinstance(m, nn.LSTM):
        for param in m.parameters():
            if len(param.shape) >= 2:
                init.orthogonal_(param.data)
            else:
                init.normal_(param.data)
    elif isinstance(m, nn.LSTMCell):
        for param in m.parameters():
            if len(param.shape) >= 2:
                init.orthogonal_(param.data)
            else:
                init.normal_(param.data)
    elif isinstance(m, nn.GRU):
        for param in m.parameters():
            if len(param.shape) >= 2:
                init.orthogonal_(param.data)
            else:
                init.normal_(param.data)
    elif isinstance(m, nn.GRUCell):
        for param in m.parameters():
            if len(param.shape) >= 2:
                init.orthogonal_(param.data)
            else:
                init.normal_(param.data)


def check_should_do_early_stopping(
    record, freeze_es_at_first, es_tolerance, acc_like=True, verbose=False,
):
    """Check should do early stopping by the record.
    
    If the metric passed in is `acc_like`, which means "the larger the better",
    this method will find the index of the maximum, if there are `es_tolerance`
    more value after the maximum, returns the index, indicating that should do
    early stopping and the best epoch index is `index`, otherwise returns 0.
    
    Otherwise, multiply -1 to each value in record and do above.

    Args:
        acc_record (dict): metric on valid for judging early stopping
        freeze_es_at_first (int): do not do early stopping at first x epoch
        es_tolerance (int): early stopping with no improvement after x epoch
        acc_like (bool): mark if the metric is like acc

    Returns:
        int: indicates should do early stopping or not,
            0 means no stopping, otherwise,
            a positive integer indicating the best epoch index.
    """
    # if not by acc-like metric, we multiply -1 to each record.
    if not acc_like:
        record = [-i for i in record]

    if len(record) < freeze_es_at_first:
        # freezing ES at the first x epochs
        return False

    n_valid_times = len(record)

    max_metric = max(record)
    
    idx_of_rightmost_max = (
        n_valid_times - 1 - record[::-1].index(max_metric)
    )

    if n_valid_times - idx_of_rightmost_max >= es_tolerance + 1:
        if verbose:
            print(
                "Early Stopping now, metric record on valid set: {}".format(
                    record,
                ),
            )
            print("The best epoch is ep{}".format(idx_of_rightmost_max))

        return idx_of_rightmost_max
    
    if verbose:
        print("\nNo stopping, Metric Record of valid:{}\n".format(record))

    return 0


class Phase(Enum):
    """Mark the training phase."""

    TRAIN = 1
    VALID = 2
    TEST = 3


def get_linear_schedule_with_warmup_ep(
    optimizer, num_warmup_epochs, total_epochs, last_epoch=-1,
):
    """Return Linear decay LambdaLR.

    :param optimizer:
    :param num_warmup_epochs:
    :param num_training_epochs:
    :param last_epoch:
    :return:
    """
    def lr_lambda(current_epoch: int):
        if current_epoch < num_warmup_epochs:
            return max(
                0.05,
                float(current_epoch) / float(max(1, num_warmup_epochs)),
            )

        epochs_left = float(total_epochs - current_epoch)
        epochs_no_wu = float(total_epochs - num_warmup_epochs)

        return max(0.0, epochs_left / epochs_no_wu)

    return LambdaLR(optimizer, lr_lambda, last_epoch)
