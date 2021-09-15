#!/usr/bin/env python
'''
component_pt
Created by Seria at 05/02/2019 1:41 PM
Email: zzqsummerai@yeah.net

                    _ooOoo_
                  o888888888o
                 o88`_ . _`88o
                 (|  0   0  |)
                 O \   。   / O
              _____/`-----‘\_____
            .’   \||  _ _  ||/   `.
            |  _ |||   |   ||| _  |
            |  |  \\       //  |  |
            |  |    \-----/    |  |
             \ .\ ___/- -\___ /. /
         ,--- /   ___\<|>/___   \ ---,
         | |:    \    \ /    /    :| |
         `\--\_    -. ___ .-    _/--/‘
   ===========  \__  NOBUG  __/  ===========

'''
# -*- coding:utf-8 -*-
from functools import partial
import torch
import torch.nn as nn
from math import ceil
import os
from ..toolkit.utility import recordConfig
from .component import Pod





class PTreshape(nn.Module):
    def __init__(self, shape, **kwargs):
        super(PTreshape, self).__init__(**kwargs)
        self.shape = shape

    def forward(self, input):
        return torch.reshape(input, self.shape)

class PTflat(nn.Module):
    def __init__(self, **kwargs):
        super(PTflat, self).__init__(**kwargs)

    def forward(self, input):
        bs = input.shape[0]
        return input.view(bs, -1)

class PTdense(nn.Module):
    def __init__(self, out_chs, use_bias, in_shape, out_shape, **kwargs):
        super(PTdense, self).__init__(**kwargs)
        self.in_shape = in_shape
        self.out_shape = out_shape
        self.fc = nn.Linear(in_shape[-1], out_chs, bias=use_bias)

    def forward(self, input):
        if self.out_shape is None:
            output = self.fc(input)
        else:
            output = input.reshape(self.in_shape)
            output = self.fc(output)
            output = output.reshape(self.out_shape)
        return output

class Duplicate(nn.Module):
    def __init__(self, **kwargs):
        super(Duplicate, self).__init__(**kwargs)

    def forward(self, input):
        return input

class PTwd(nn.Module):
    def __init__(self, **kwargs):
        super(PTwd, self).__init__(**kwargs)

    def forward(self, penalty):
        return torch.zeros(1)

class PTsftmxe(nn.Module):
    def __init__(self, is_one_hot, **kwargs):
        super(PTsftmxe, self).__init__(**kwargs)
        self.ioh = is_one_hot
        self.cost = nn.CrossEntropyLoss()

    def forward(self, input, label):
        if self.ioh:
            label = torch.argmax(label, dim=-1)
        return self.cost(input, label)

class AccuracyCLS(nn.Module):
    def __init__(self, multi_class, is_one_hot, **kwargs):
        super(AccuracyCLS, self).__init__(**kwargs)
        if multi_class:
            assert not is_one_hot
        self.mulcls = multi_class
        self.onehot = is_one_hot

    def forward(self, input, label):
        if self.mulcls:
            pred = torch.round(input)
            correct = torch.mean((pred == label).type(torch.FloatTensor), dim=-1)
            return torch.mean((correct == 1).type(torch.FloatTensor))
        else:
            if self.onehot:
                label = torch.argmax(label, dim=-1)
            pred = torch.argmax(input, dim=-1)
            return torch.mean((pred == label).type(torch.FloatTensor))

class ComponentPT(object):
    def __init__(self, channel_major=True, time_major=False):
        self.channel_major = channel_major
        self.time_major = time_major
        self.warehouse = ['CONV', 'CONV_TRANS', 'CONV_SEP',
                          'SIGMOID', 'TANH', 'SOFTMAX', 'RELU', 'RELU_LEAKY', 'RELU_EXP',
                          'MAX_POOL', 'AVG_POOL',
                          'DROPOUT', 'BATCH_NORM', 'EMBEDDING',
                          'RESHAPE', 'FLAT', 'SLICE',
                          'CLIP', 'DENSE',
                          'RESIZE',
                          'DUPLICATE', 'CONVERT',
                          'WEIGHT_DECAY', 'SIGM_XENTROPY', 'SFTM_XENTROPY', 'MSE', 'MAE',
                          'MOMENTUM', 'NESTEROV', 'ADAM']
        # Convolution
        self.CONV = self.conv
        # self.TRANS_CONV = self.trans_conv
        self.SEP_CONV = 4
        # Activation
        self.SIGMOID = self.sigmoid
        self.TANH = self.tanh
        self.SOFTMAX = self.softmax
        self.RELU = self.relu
        self.LRELU = self.relu_leaky
        # self.ERELU = self.relu_exp
        # Pooling
        self.MAX_POOL = self.max_pool
        self.AVG_POOL = self.avg_pool
        # Distributing
        self.DROPOUT = self.dropout
        self.BATCH_NORM = self.batch_norm
        # self.EMBEDDING = self.embedding
        # Reshape
        # self.RESHAPE = self.reshape
        self.FLAT = self.flat
        # self.SLICE = self.slice
        # self.PAD = self.pad
        # Arithmetic
        # self.CLIP = self.clip
        self.DENSE = self.dense
        # self.ARGMAX = self.argmax
        # Image Manipulation
        # self.RESIZE = self.resize
        # Copy or Rename
        self.DUPLICATE = self.duplicate
        # self.CONVERT = self.convert
        # Loss
        self.WEIGHT_DECAY = self.weight_decay
        self.SIGM_XE = self.sigm_xentropy
        self.SFTM_XE = self.sftm_xentropy
        self.MSE = self.mse
        self.MAE = self.mae
        # Optimizer
        self.MOMENTUM = self.momentum
        self.NESTEROV = self.nesterov
        self.ADAM = self.adam
        # Metric
        self.ACC_CLS = self.accuracy_cls



    def addComp(self, name, comp, is_ready=False):
        name = name.upper()
        if name in self.warehouse:
            raise Exception('NEBULAE ERROR ⨷ %s is an existing component in warehouse.' % name)
        else:
            self.warehouse.append(name)
        if is_ready:
            def customizedComp(name):
                return Pod(partial(comp.component, name=name), comp.symbol, name, comp.message, comp.info)
        else:
            assert not isinstance(comp.component, list)
            def customizedComp(**kwargs):
                message = []
                # check input so as to update message
                for s, sym in enumerate(comp.symbol):
                    if sym in kwargs:
                        message.append(kwargs[sym])
                    else:
                        message.append(comp.message[s])
                info = {}
                for k, v in comp.info.items():
                    info[k] = kwargs.get(k, v)
                return Pod(partial(comp.component, **kwargs), comp.symbol, kwargs['name'], message, info)
        exec('self.%s = customizedComp' % name)

    # ------------------------------------ Convolution ------------------------------------ #

    def _initialize(self, layer, initializer, parameter, regularizer):
        layer = (layer.weight, layer.bias)
        for elt, iniz, param, regz in zip(layer, initializer, parameter, regularizer):
            if iniz == 'xavier':
                if param is None:
                    param = 'normal'
                else:
                    if param=='normal':
                        nn.init.xavier_normal_(elt)
                    elif param=='uniform':
                        nn.init.xavier_uniform_(elt)
                    else:
                        raise Exception(
                            'NEBULAE ERROR ⨷ %s-%s initializer is not defined or supported.' % (iniz, param))
            elif iniz == 'uniform':
                if param is None:
                    param = [-0.5, 0.5]
                nn.init.uniform_(elt, a=param[0], b=param[1])
            elif iniz == 'normal':
                if param is None:
                    param = [0, 0.1]
                nn.init.normal_(elt, param[0], param[1])
            elif iniz == 'zero':
                nn.init.zeros_(elt)
            elif iniz == 'one':
                nn.init.ones_(elt)
            elif iniz is None:
                continue
            else:
                raise Exception('NEBULAE ERROR ⨷ %s initializer is not defined or supported.' % iniz)

            if regz == 'l2':
                pass
            else:
                raise Exception('NEBULAE ERROR ⨷ %s regularizer is not defined or supported.' % regularizer)

    def conv(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._conv, **kwargs), ['input'], kwargs['name'], [message],
                   {'type': 'CONV', 'cmajor': self.channel_major, 'out_chs': kwargs.get('out_chs', None),
                    'kernel': kwargs.get('kernel', None), 'stride': kwargs.get('stride', (1, 1)),
                    'auto_pad': kwargs.get('auto_pad', True)})
    def _conv(self, name, input, out_chs, kernel, w_init='xavier', w_param=None, b_init=None, b_param=None,
                w_reg='l2', b_reg='l2', stride=(1, 1), dilation=(1, 1), group=1, auto_pad=True):
        ch_err = Exception('NEBULAE ERROR ⨷ %s NHWC-type tensor is not supported in PyTorch core.')
        dim = len(kernel)
        if dim == 1:
            conv_func = nn.Conv1d
            if self.channel_major:
                dform = 'NCW'
            else:
                dform = 'NWC'
                raise ch_err
        elif dim == 2:
            conv_func = nn.Conv2d
            if self.channel_major:
                dform = 'NCHW'
            else:
                dform = 'NHWC'
                raise ch_err
        elif dim == 3:
            conv_func = nn.Conv3d
            if self.channel_major:
                dform = 'NCDHW'
            else:
                dform = 'NDHWC'
                raise ch_err
        else:
            raise Exception('NEBULAE ERROR ⨷ %d-d convolution is not supported.' % dim)

        if self.channel_major:
            size = input[2:]
            in_chs = input[1]
        else:
            size = input[1:-1]
            in_chs = input[-1]
        if auto_pad:
            padding = []
            for d in range(dim):
                padding.append(ceil(((ceil(size[d] / stride[d]) - 1) * stride[d] + kernel[d] + (dilation[d] - 1) * (
                kernel[d] - 1) - size[d]) / 2))
        else:
            padding = dim * [0]
        convolution = conv_func(in_chs, out_chs, kernel, stride=stride, padding=padding,
                                dilation=dilation, groups=group, bias=True)
        self._initialize(convolution, (w_init, b_init), (w_param, b_param), (w_reg, b_reg))
        return convolution

    # ------------------------------------ Activation ------------------------------------ #

    def sigmoid(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._sigmoid, **kwargs), ['input'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _sigmoid(self, name, input):
        return nn.Sigmoid()

    def tanh(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._tanh, **kwargs), ['input'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _tanh(self, name, input):
        return nn.Tanh()

    def softmax(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._tanh, **kwargs), ['input'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _softmax(self, name, input):
        return nn.Softmax()

    def relu(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._relu, **kwargs), ['input'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _relu(self, name, input):
        return nn.ReLU()

    def relu_leaky(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._relu_leaky, **kwargs), ['input'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _relu_leaky(self, name, input, alpha=0.2):
        return nn.LeakyReLU(alpha)

    # ------------------------------------ Distributing ------------------------------------ #

    def dropout(self, **kwargs):
        message = []
        message.append(kwargs.get('input', '_INPUT'))
        message.append(kwargs.get('is_train', '_IS_TRAIN'))
        return Pod(partial(self._dropout, **kwargs), ['input', 'is_train'], kwargs['name'], message, {'type': 'DROP'})
    def _dropout(self, name, input, p_drop, is_train):
        return nn.Dropout(p_drop)

    def batch_norm(self, **kwargs):
        message = []
        message.append(kwargs.get('input', '_INPUT'))
        message.append(kwargs.get('is_train', '_IS_TRAIN'))
        return Pod(partial(self._batch_norm, **kwargs), ['input', 'is_train'], kwargs['name'], message,
                   {'type': 'BN', 'cmajor': self.channel_major})
    def _batch_norm(self, name, input, is_train, beta=False, gamma=False):
        if self.channel_major:
            num_feat = input[1]
        else:
            raise Exception('NEBULAE ERROR ⨷ %s NHWC-type tensor is not supported in PyTorch core.')
        dim = len(input)-2
        if dim == 1:
            bn_func = nn.BatchNorm1d
        elif dim == 2:
            bn_func = nn.BatchNorm2d
        elif dim == 3:
            bn_func = nn.BatchNorm3d
        else:
            raise Exception('NEBULAE ERROR ⨷ %d-d BN is not supported.' % dim)
        return bn_func(num_feat, affine=beta or gamma)

    # def embedding(self, **kwargs):
    #     message = kwargs.get('input', '_INPUT')
    #     return Pod(partial(self._embedding, **kwargs), ['input'], kwargs['name'], [message])
    # def _embedding(self, name, input, vocabulary, vec_dims, w_init='xavier', w_param=None):
    #     embd_vec = self._createVar(name+'_vec', [vocabulary, vec_dims], w_init, w_param)
    #     return tf.nn.embedding_lookup(embd_vec, input, name=name)

    # ------------------------------------ Pooling ------------------------------------ #

    def max_pool(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._max_pool, **kwargs), ['input'], kwargs['name'], [message],
                   {'type': 'POOL', 'cmajor': self.channel_major, 'kernel': kwargs.get('kernel', (2, 2)),
                    'stride': kwargs.get('stride', (2, 2)), 'auto_pad': kwargs.get('auto_pad', True),
                    'if_global': kwargs.get('if_global', False)})
    def _max_pool(self, name, input, kernel=(2, 2), stride=(2, 2), auto_pad=True, if_global=False):
        dim = len(kernel)
        if dim == 1:
            pool_func = nn.MaxPool1d
            if self.channel_major:
                dform = 'NCW'
            else:
                dform = 'NWC'
                raise Exception('NEBULAE ERROR ⨷ %s NHWC-type tensor is not supported in PyTorch core.')
        elif dim == 2:
            pool_func = nn.MaxPool2d
            if self.channel_major:
                dform = 'NCHW'
            else:
                dform = 'NHWC'
                raise Exception('NEBULAE ERROR ⨷ %s NHWC-type tensor is not supported in PyTorch core.')
        elif dim == 3:
            pool_func = nn.MaxPool3d
            if self.channel_major:
                dform = 'NCDHW'
            else:
                dform = 'NDHWC'
                raise Exception('NEBULAE ERROR ⨷ %s NHWC-type tensor is not supported in PyTorch core.')
        else:
            raise Exception('NEBULAE ERROR ⨷ %d-d convolution is not supported.' % dim)

        if self.channel_major:
            size = input[2:]
        else:
            size = input[1:-1]
        if if_global:
            kernel = size
            padding = dim * [0]
        else:
            if auto_pad:
                padding = []
                for d in range(dim):
                    padding.append(ceil(((ceil(size[d] / stride[d]) - 1) * stride[d] + kernel[d] - size[d]) / 2))
            else:
                padding = dim * [0]
        if dim == 1:
            kernel = kernel[0]
            stride = stride[0]
            padding = padding[0]
        return pool_func(kernel_size=kernel, stride=stride, padding=padding)

    def avg_pool(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._avg_pool, **kwargs), ['input'], kwargs['name'], [message],
                   {'type': 'POOL', 'cmajor': self.channel_major, 'kernel': kwargs.get('kernel', (2, 2)),
                    'stride': kwargs.get('stride', (2, 2)), 'auto_pad': kwargs.get('auto_pad', True),
                    'if_global': kwargs.get('if_global', False)})
    def _avg_pool(self, name, input, kernel=(2, 2), stride=(2, 2), auto_pad=True, if_global=False):
        dim = len(kernel)
        if dim == 1:
            pool_func = nn.AvgPool1d
            if self.channel_major:
                dform = 'NCW'
            else:
                dform = 'NWC'
                raise Exception('NEBULAE ERROR ⨷ %s NHWC-type tensor is not supported in PyTorch core.')
        elif dim == 2:
            pool_func = nn.AvgPool2d
            if self.channel_major:
                dform = 'NCHW'
            else:
                dform = 'NHWC'
                raise Exception('NEBULAE ERROR ⨷ %s NHWC-type tensor is not supported in PyTorch core.')
        elif dim == 3:
            pool_func = nn.AvgPool3d
            if self.channel_major:
                dform = 'NCDHW'
            else:
                dform = 'NDHWC'
                raise Exception('NEBULAE ERROR ⨷ %s NHWC-type tensor is not supported in PyTorch core.')
        else:
            raise Exception('NEBULAE ERROR ⨷ %d-d convolution is not supported.' % dim)

        if self.channel_major:
            size = input[2:]
        else:
            size = input[1:-1]
        if if_global:
            kernel = size
            padding = dim * [0]
        else:
            if auto_pad:
                padding = []
                for d in range(dim):
                    padding.append(ceil(((ceil(size[d] / stride[d]) - 1) * stride[d] + kernel[d] - size[d]) / 2))
            else:
                padding = dim * [0]
        if dim == 1:
            kernel = kernel[0]
            stride = stride[0]
            padding = padding[0]
        return pool_func(kernel_size=kernel, stride=stride, padding=padding)

    # ------------------------------------ Reshape ------------------------------------ #

    def reshape(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._reshape, **kwargs), ['input'], kwargs['name'], [message],
                   {'type': 'RESHAPE', 'shape': kwargs.get('shape', None)})
    def _reshape(self, name, input, shape):
        return PTreshape(shape)

    def flat(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._flat, **kwargs), ['input'], kwargs['name'], [message], {'type': 'FLAT'})
    def _flat(self, name, input):
        return PTflat()
    #
    # def slice(self, **kwargs):
    #     message = kwargs.get('input', '_INPUT')
    #     return Pod(partial(self._slice, **kwargs), ['input'], kwargs['name'], [message])
    # def _slice(self, name, input, indices):
    #     for d in range(len(indices)):
    #         output = input[indices[d][0]:indices[d][1]]
    #     return tf.identity(output, name)
    #
    # def pad(self, **kwargs):
    #     message = kwargs.get('input', '_INPUT')
    #     return Pod(partial(self._pad, **kwargs), ['input'], kwargs['name'], [message])
    # def _pad(self, name, input, margin, fill_in=0):
    #     return tf.pad(input, margin, constant_values=fill_in, name=name)
    #
    # # -------------------------------------- Arithmetic -------------------------------------- #
    #
    # def clip(self, **kwargs):
    #     message = kwargs.get('input', '_INPUT')
    #     return Pod(partial(self._clip, **kwargs), ['input'], kwargs['name'], [message])
    # def _clip(self, name, input, min_max_vals):
    #     return tf.clip_by_value(input, min_max_vals[0], min_max_vals[1], name)

    def dense(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._dense, **kwargs), ['input'], kwargs['name'], [message],
                   {'type': 'DENSE', 'out_chs': kwargs.get('out_chs', None), 'axis': kwargs.get('axis', -1)})
    def _dense(self, name, input, out_chs, axis=-1, w_init='xavier', w_param=None,
               b_init='zero', b_param=None, w_reg='l2', b_reg='l2'):
        if axis == 0:
            raise Exception('NEBULAE ERROR ⨷ you cannot apply dense layer along batch axis.')
        elif axis == -1:
            in_shape = list(input)
            out_shape = None
        else:
            size = list(input)
            channel = (size[axis],)
            del size[axis]
            size[0] = -1
            in_shape = tuple(size) + channel
            out_shape = list(input)
            out_shape[0] = -1
            out_shape[axis] = out_chs
            out_shape = tuple(out_shape)

        if not b_init is None:
            use_bias = True
        else:
            use_bias = False
        fully_connect = PTdense(out_chs, use_bias, in_shape, out_shape)
        self._initialize(fully_connect.fc, (w_init, b_init), (w_param, b_param), (w_reg, b_reg))
        return fully_connect

    # def argmax(self, **kwargs):
    #     message = kwargs.get('input', '_INPUT')
    #     return Pod(partial(self._argmax, **kwargs), ['input'], kwargs['name'], [message])
    # def _argmax(self, name, input, axis):
    #     return tf.argmax(input, axis, name=name)
    #
    # # ------------------------------------ Image Manipulation ------------------------------------ #
    #
    # def resize(self, **kwargs):
    #     message = kwargs.get('input', '_INPUT')
    #     return Pod(partial(self._resize, **kwargs), ['input'], kwargs['name'], [message])
    # def _resize(self, name, input, size, method='bilinear'):
    #     if method == 'bilinear':
    #         return tf.image.resize_bilinear(input, size, name=name)
    #     elif method == 'bicubic':
    #         return tf.image.resize_bicubic(input, size, name=name)
    #     elif method == 'crop':
    #         return tf.image.resize_image_with_crop_or_pad(input, size, name=name)
    #     else:
    #         raise KeyError('NEBULAE ERROR ⨷ %s is not a legal resize method.' % method)
    #
    #
    # # ------------------------------------ Redefine or Rename ------------------------------------ #
    #
    def duplicate(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._duplicate, **kwargs), ['input'], kwargs['name'], [message], {'type': 'DUP'})
    def _duplicate(self, name, input):
        return Duplicate()
    #
    # def convert(self, **kwargs):
    #     message = kwargs.get('input', '_INPUT')
    #     return Pod(partial(self._convert, **kwargs), ['input'], kwargs['name'], [message])
    # def _convert(self, name, input, dtype, trainable=False):
    #     '''
    #     convert data type or convert list/numpy array to tensor
    #     :param name:
    #     :param input: input tensor / list / numpy array
    #     :param dtype:
    #     :param trainable: if tensor is trainable
    #     :return: tensor
    #     '''
    #     if isinstance(input, (tf.Tensor, tf.SparseTensor, tf.Variable)):
    #         return tf.cast(input, tf.as_dtype(dtype), name=name)
    #     else:
    #         return tf.Variable(input, trainable=trainable, name=name)

    # ------------------------------------ Loss ------------------------------------ #

    def weight_decay(self, **kwargs):
        return Pod(partial(self._weight_decay, **kwargs), ['penalty'], kwargs['name'],
                   [torch.ones(1) * kwargs['penalty']], {'type': 'LOSS'})
    def _weight_decay(self, name, penalty, decay_scope=None):
        if not decay_scope is None:
            raise Exception('NEBULAE ERROR ⨷ weight decay cannot be manipulated explicitly in PyTorch core.')
        return PTwd()

    def sigm_xentropy(self, **kwargs):
        message = []
        message.append(kwargs.get('input', '_INPUT'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._sigm_xentropy, **kwargs), ['input', 'label'], kwargs['name'], message, {'type': 'LOSS'})
    def _sigm_xentropy(self, name, input, label):
        return nn.BCEWithLogitsLoss()

    def sftm_xentropy(self, **kwargs):
        message = []
        message.append(kwargs.get('input', '_INPUT'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._sftm_xentropy, **kwargs), ['input', 'label'], kwargs['name'], message, {'type': 'LOSS'})
    def _sftm_xentropy(self, name, input, label, is_one_hot):
        return PTsftmxe(is_one_hot)

    def mse(self, **kwargs):
        message = []
        message.append(kwargs.get('input', '_INPUT'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._mse, **kwargs), ['input', 'label'], kwargs['name'], message, {'type': 'LOSS'})
    def _mse(self, name, input, label):
        return nn.MSELoss()

    def mae(self, **kwargs):
        message = []
        message.append(kwargs.get('input', '_INPUT'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._mae, **kwargs), ['input', 'label'], kwargs['name'], message, {'type': 'LOSS'})
    def _mae(self, name, input, label):
        return nn.L1Loss()

    # ------------------------------------ Optimizer ------------------------------------ #

    def _lrStrategy(self, optimizer, lr, lr_decay, miles, param):
        if lr_decay == 'step':
            return torch.optim.lr_scheduler.StepLR(optimizer, miles, gamma=param)
        elif lr_decay == 'poly':
            lr_update = lambda epoch: (1.001 - epoch / miles) ** param
            return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_update)
        elif lr_decay == 'cosine':
            return torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=miles, eta_min=lr*0.001)
        elif lr_decay == 'exp':
            lr_update = lambda epoch: param ** (epoch / miles)
            return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_update)
        elif lr_decay == 'wavy':
            lr_update = lambda x: param ** (x - 1)
            return torch.optim.lr_scheduler.CyclicLR(optimizer, lr/2, lr,
                 step_size_up=miles, scale_fn=lr_update, scale_mode='cycle')
        else:
            raise KeyError('NEBULAE ERROR ⨷ %s decay is not supported or defined.' % lr_decay)

    def _selectParam(self, global_var, update_scope, ignore_name):
        update_var = []
        if ignore_name is None:
            ignore_name = []
        for l, p in global_var.items():
            if (update_scope is None or l.startswith(update_scope)) and (l not in ignore_name):
                update_var.extend(list(p))
        return update_var

    def momentum(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._momentum, **kwargs), ['input', 'media'], kwargs['name'], [message, '_MEDIA'], {'type': 'OPTZ'})
    def _momentum(self, name, lr, input=None, mmnt=0.9, update_scope=None, ignore_name=None,
                  lr_decay=None, lr_miles=None, decay_param=None, grad_limit=None, media=None):
        recordConfig(os.path.join(os.getcwd(), 'temp_config.json'),
                     {'lr': lr, 'mmnt': mmnt, 'update_scope': update_scope, 'ignore_name': ignore_name,
                      'lr_decay': lr_decay, 'lr_miles': lr_miles, 'decay_param': decay_param, 'grad_limit': grad_limit})
        # N.B. media is network and wd factor
        mod_params, wd = media
        wd = wd.numpy().tolist()[0]
        update_params = self._selectParam(mod_params, update_scope, ignore_name)
        nn.utils.clip_grad_value_(update_params, grad_limit)
        optz = torch.optim.SGD(update_params, lr=lr, momentum=mmnt, weight_decay=wd)
        if isinstance(lr_decay, str):
            optz = self._lrStrategy(optz, lr, lr_decay, lr_miles, decay_param)
        return optz

    def nesterov(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._nesterov, **kwargs), ['input', 'media'], kwargs['name'], [message, '_MEDIA'], {'type': 'OPTZ'})
    def _nesterov(self, name, lr, input=None, mmnt=0.9, update_scope=None, ignore_name=None,
                  lr_decay=None, lr_miles=None, decay_param=None, grad_limit=None, media=None):

        recordConfig(os.path.join(os.getcwd(), 'temp_config.json'),
                     {'lr': lr, 'mmnt': mmnt, 'update_scope': update_scope, 'ignore_name': ignore_name,
                      'lr_decay': lr_decay, 'lr_miles': lr_miles, 'decay_param': decay_param, 'grad_limit': grad_limit})
        # N.B. media is network  and wd factor
        mod_params, wd = media
        wd = wd.numpy().tolist()[0]
        update_params = self._selectParam(mod_params, update_scope, ignore_name)
        nn.utils.clip_grad_value_(update_params, grad_limit)
        optz = torch.optim.SGD(update_params, lr=lr, momentum=mmnt, weight_decay=wd, nesterov=True)
        if isinstance(lr_decay, str):
            optz = self._lrStrategy(optz, lr, lr_decay, lr_miles, decay_param)
        return optz

    def adam(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._adam, **kwargs), ['input', 'media'], kwargs['name'], [message, '_MEDIA'], {'type': 'OPTZ'})
    def _adam(self, name, lr, input=None, mmnt1=0.9, mmnt2=0.999, update_scope=None, ignore_name=None,
                  lr_decay=None, lr_miles=None, decay_param=None, grad_limit=None, media=None):
        recordConfig(os.path.join(os.getcwd(), 'temp_config.json'),
                     {'lr': lr, 'mmnt1': mmnt1, 'mmnt2': mmnt2, 'update_scope': update_scope,
                      'ignore_name': ignore_name, 'lr_decay': lr_decay, 'lr_miles': lr_miles,
                      'decay_param': decay_param, 'grad_limit': grad_limit})
        # N.B. media is network and wd factor
        mod_params, wd = media
        wd = wd.numpy().tolist()[0]
        update_params = self._selectParam(mod_params, update_scope, ignore_name)
        nn.utils.clip_grad_value_(update_params, grad_limit)
        optz = torch.optim.Adam(update_params, lr=lr, betas=(mmnt1, mmnt2), weight_decay=wd)
        if isinstance(lr_decay, str):
            optz = self._lrStrategy(optz, lr, lr_decay, lr_miles, decay_param)
        return optz

    # ------------------------------------ Metric ------------------------------------ #

    def accuracy_cls(self, **kwargs):
        message = []
        message.append(kwargs.get('input', '_INPUT'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._accuracy_cls, **kwargs), ['input', 'label'], kwargs['name'], message, {'type': 'ACC'})
    def _accuracy_cls(self, name, input, label, multi_class=False, is_one_hot=False):
        return AccuracyCLS(multi_class, is_one_hot)