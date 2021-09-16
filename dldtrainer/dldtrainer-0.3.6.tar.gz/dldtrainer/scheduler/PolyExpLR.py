# -*-coding: utf-8 -*-
"""
    @Author : panjq
    @E-mail : pan_jinquan@163.com
    @Date   : 2021-07-28 15:32:44
"""

import torch
import torch.optim as optim
import torch.nn as nn
import numpy as np
from .WarmUpLR import WarmUpLR
from ..callbacks.callbacks import Callback


class PolyExpLR(Callback):
    def __init__(self,
                 optimizer,
                 epochs,
                 num_steps,
                 lr_init=0.01,
                 num_warn_up=0,
                 gamma=0.1):
        """
        a poly exponent scheduler about steps, not epochs.
        :param optimizer: ex. optim.SGD
        :param epochs:
        :param num_steps: 一个epoch的迭代次数，len(self.train_dataloader)
        :param milestones:  (list): List of epoch indices. Must be increasing.
        :param lr_init: lr_max is init lr.
        :param num_warn_up:
        :param gamma (float): Multiplicative factor of learning rate decay.Default: 0.1.
        """
        self.optimizer = optimizer
        self.epochs = epochs
        self.num_steps = num_steps
        self.max_step = epochs * self.num_steps
        self.lr_init = lr_init
        self.epoch = 0
        self.gamma = gamma
        self.warm_up = WarmUpLR(optimizer,
                                num_steps=self.num_steps,
                                lr_init=lr_init,
                                num_warn_up=num_warn_up)
        super(PolyExpLR, self).__init__()

    def get_lr(self, epoch):
        lr = self.optimizer.param_groups[0]["lr"]
        cur_step = epoch * self.num_steps
        lr = self.lr_init * pow((1 - cur_step / self.max_step), self.gamma)
        return lr

    def set_lr(self, lr):
        for param_group in self.optimizer.param_groups:
            param_group["lr"] = lr

    def set_poly_lr(self, epoch):
        lr = self.get_lr(epoch)
        self.set_lr(lr)

    def on_epoch_begin(self, epoch, logs: dict = {}):
        self.epoch = epoch
        self.set_poly_lr(epoch)

    def on_batch_end(self, batch, logs: dict = {}):
        self.step(epoch=self.epoch, step=batch)

    def step(self, epoch=0, step=0):
        # step每次迭代都会调用，比较耗时，建议与step无关的操作放在on_epoch_begin中
        self.warm_up.step(epoch, step)