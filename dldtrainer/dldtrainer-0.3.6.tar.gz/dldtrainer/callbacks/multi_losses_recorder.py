# -*-coding: utf-8 -*-
"""
    @Author : panjq
    @E-mail : pan_jinquan@163.com
    @Date   : 2021-07-28 11:32:42
"""
import numpy as np
import torch
from ..metric.eval_tools.metrics import AverageMeter
from ..callbacks import callbacks


class MultiLossesRecorder(callbacks.Callback):
    def __init__(self, indicators: dict):
        """
        用于记录多个loss的值,并自动计算法total_loss
        :param indicators: 指标名称(dict),
               如indicators = {"loss": {"loss1", "loss2"}}，
               其中"loss1", "loss2"是run_step()中返回的loss值:
               ==> losses = {"loss1": loss1, "loss2": loss2}
               ==> return outputs, losses
        """
        super(MultiLossesRecorder, self).__init__()
        self.indicators = indicators
        self.train_losses = {}
        self.test_losses = {}
        for name, indicator in self.indicators.items():
            for k in indicator:
                self.train_losses[k] = AverageMeter()
                self.test_losses[k] = AverageMeter()

    def on_test_begin(self, logs: dict = {}):
        for name, indicator in self.indicators.items():
            for k in indicator:
                self.train_losses[k].reset()
                self.test_losses[k].reset()

    @staticmethod
    def summary(phase, average_meter: dict, indicators: dict, losses, logs: dict = {}):
        logs[phase] = logs[phase] if phase in logs else {}
        for name, indicator in indicators.items():
            scalar_dict = {}
            for k in indicator:
                average_meter[k].update(losses[k].data.item())
                # average_meter[k].update(losses[k].data.item(), labels.size(0))
                scalar_dict[k] = average_meter[k].avg
            if len(indicator) > 1:
                scalar_dict["total_{}".format(name)] = sum(scalar_dict.values())
            logs[phase][name] = scalar_dict

    def on_train_summary(self, inputs, outputs, losses, epoch, step, logs: dict = {}):
        self.summary(phase="train", average_meter=self.train_losses,
                     indicators=self.indicators, losses=losses, logs=logs)

    def on_test_summary(self, inputs, outputs, losses, epoch, batch, logs: dict = {}):
        self.summary(phase="test", average_meter=self.test_losses,
                     indicators=self.indicators, losses=losses, logs=logs)
