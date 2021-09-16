#!/usr/bin/env python
'''
component_tf
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
from mxnet.gluon import nn, rnn, loss, Trainer, HybridBlock, ParameterDict
from mxnet import nd, init, autograd, lr_scheduler
from math import ceil, cos, pi
import os
from ..toolkit.utility import recordConfig
from .component import Pod



class OffTheShelfMX(HybridBlock):
    def __init__(self, **kwargs):
        prefix = kwargs.get('prefix', None)
        super(OffTheShelfMX, self).__init__(prefix=prefix)

    def run(self, *args):
        raise NotImplementedError

    def hybrid_forward(self, F, *args):
        return self.run(*args)

class CosineAnnealingSchedule():
    def __init__(self, min_lr, max_lr, cycle_length):
        """
        min_lr: lower bound for learning rate (float)
        max_lr: upper bound for learning rate (float)
        cycle_length: iterations between start and finish (int)
        """
        self.min_lr = min_lr
        self.max_lr = max_lr
        self.cycle_length = cycle_length

    def __call__(self, iteration):
        if iteration <= self.cycle_length:
            unit_cycle = (1 + cos(iteration * pi / self.cycle_length)) / 2
            adjusted_cycle = (unit_cycle * (self.max_lr - self.min_lr)) + self.min_lr
            return adjusted_cycle
        else:
            return self.min_lr

class CyclicalSchedule():
    def __init__(self, schedule_class, cycle_length, cycle_length_decay=1, cycle_magnitude_decay=1, **kwargs):
        """
        schedule_class: class of schedule, expected to take `cycle_length` argument
        cycle_length: iterations used for initial cycle (int)
        cycle_length_decay: factor multiplied to cycle_length each cycle (float)
        cycle_magnitude_decay: factor multiplied learning rate magnitudes each cycle (float)
        kwargs: passed to the schedule_class
        """
        self.schedule_class = schedule_class
        self.length = cycle_length
        self.length_decay = cycle_length_decay
        self.magnitude_decay = cycle_magnitude_decay
        self.kwargs = kwargs

    def __call__(self, iteration):
        cycle_idx = 0
        cycle_length = self.length
        idx = self.length
        while idx <= iteration:
            cycle_length = ceil(cycle_length * self.length_decay)
            cycle_idx += 1
            idx += cycle_length
        cycle_offset = iteration - idx + cycle_length

        schedule = self.schedule_class(cycle_length=cycle_length, **self.kwargs)
        return schedule(cycle_offset) * self.magnitude_decay**cycle_idx

class MXsigmoid(HybridBlock):
    def __init__(self, **kwargs):
        super(MXsigmoid, self).__init__(**kwargs)

    def hybrid_forward(self, F, input):
        return F.sigmoid(input)

class MXtanh(HybridBlock):
    def __init__(self, **kwargs):
        super(MXtanh, self).__init__(**kwargs)

    def hybrid_forward(self, F, input):
        return F.tanh(input)

class MXsoftmax(HybridBlock):
    def __init__(self, **kwargs):
        super(MXsoftmax, self).__init__(**kwargs)

    def hybrid_forward(self, F, input):
        return F.softmax(input)

class MXrelu(HybridBlock):
    def __init__(self, **kwargs):
        super(MXrelu, self).__init__(**kwargs)

    def hybrid_forward(self, F, input):
        return F.relu(input)

class MXreshape(HybridBlock):
    def __init__(self, *shape, **kwargs):
        super(MXreshape, self).__init__(**kwargs)
        self.shape = shape

    def hybrid_forward(self, F, input):
        return input.reshape(*self.shape)

class MXdense(HybridBlock):
    def __init__(self, out_chs, use_bias, w_init, b_init, in_shape, out_shape, **kwargs):
        super(MXdense, self).__init__(**kwargs)
        self.in_shape = in_shape
        self.out_shape = out_shape
        self.fc = nn.Dense(out_chs, use_bias=use_bias, flatten=False, weight_initializer=w_init, bias_initializer=b_init)

    def hybrid_forward(self, F, input):
        if self.in_shape is None:
            output = self.fc(input)
        else:
            output = input.reshape(self.in_shape)
            output = self.fc(output)
            output = output.reshape(self.out_shape)
        return output

class Duplicate(HybridBlock):
    def __init__(self, **kwargs):
        super(Duplicate, self).__init__(**kwargs)

    def hybrid_forward(self, F, input):
        return input

class MXwd(HybridBlock):
    def __init__(self, **kwargs):
        super(MXwd, self).__init__(**kwargs)

    def hybrid_forward(self, F, penalty):
        return F.zeros((1))

class MXmse(HybridBlock):
    def __init__(self, **kwargs):
        super(MXmse, self).__init__(**kwargs)

    def hybrid_forward(self, F, input, label):
        return (input-label)**2

class MXmae(HybridBlock):
    def __init__(self, **kwargs):
        super(MXmae, self).__init__(**kwargs)

    def hybrid_forward(self, F, input, label):
        return F.abs(input-label)

class MXsigmxe(HybridBlock):
    def __init__(self, **kwargs):
        super(MXsigmxe, self).__init__(**kwargs)
        self.cost = loss.SigmoidBCELoss()

    def hybrid_forward(self, F, input, label):
        return F.mean(self.cost(input, label))

class MXsftmxe(HybridBlock):
    def __init__(self, is_one_hot, **kwargs):
        super(MXsftmxe, self).__init__(**kwargs)
        self.cost = loss.SoftmaxCELoss(sparse_label=not is_one_hot)

    def hybrid_forward(self, F, input, label):
        return F.mean(self.cost(input, label))

class MX(HybridBlock):
    def __init__(self, **kwargs):
        super(MX, self).__init__(**kwargs)

    def hybrid_forward(self, F, input):
        return nd.sigmoid(input)

class AccuracyCLS(HybridBlock):
    def __init__(self, multi_class, is_one_hot, **kwargs):
        super(AccuracyCLS, self).__init__(**kwargs)
        if multi_class:
            assert not is_one_hot
        self.mulcls = multi_class
        self.onehot = is_one_hot

    def hybrid_forward(self, F, input, label):
        if self.mulcls:
            pred = F.round(input)
            correct = F.mean(pred == label, axis=-1)
            return F.mean(correct == 1)
        else:
            if self.onehot:
                label = F.argmax(label, axis=-1)
            pred = F.argmax(input, axis=-1)
            return F.mean(pred == label)

class ComponentMX(object):
    def __init__(self, channel_major=True, time_major=False):
        self.channel_major = channel_major
        self.time_major = time_major
        self.warehouse = ['CONV', 'TRANS_CONV', 'SEP_CONV',
                          'SIGMOID', 'TANH', 'SOFTMAX', 'RELU', 'RELU_LEAKY', 'RELU_EXP',
                          'MAX_POOL', 'AVG_POOL',
                          'DROPOUT', 'BATCH_NORM', 'EMBEDDING',
                          'RESHAPE', 'FLAT', 'SLICE',
                          'CLIP', 'DENSE',
                          'RESIZE',
                          'DUPLICATE', 'CONVERT',
                          'WEIGHT_DECAY', 'SIGM_XE', 'SFTM_XE', 'MSE', 'MAE',
                          'MOMENTUM', 'NESTEROV', 'ADAM']
        # Convolution
        self.CONV = self.conv
        self.TRANS_CONV = self.trans_conv
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
        self.RESHAPE = self.reshape
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
        # Wrapped Net
        # self.RNN = self.rnn
        # self.LSTM = self.lstm
        # self.BILSTM = self.bilstm
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

    @staticmethod
    def doff(name):
        return os.path.basename(name)

    @staticmethod
    def cap(name, scope):
        return scope + ':' + name

    def remodel(self, name, comp, is_ready=False):
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

    def new(self, name, comp, *exec_args, out_shape):
        '''
        exec_args: (str,) input tensor names
        out_shape: output shape with batch size as -1
        '''
        name = name.upper()
        if name in self.warehouse:
            raise Exception('NEBULAE ERROR ⨷ %s is an existing component in warehouse.' % name)

        def newComp(**kwargs):
            message = []
            init_args = {}
            for k in kwargs:
                if k in exec_args:
                    message.append(kwargs[k])
                else:
                    init_args[k] = kwargs[k]
            return Pod(partial(_newComp, **init_args), list(exec_args), kwargs['name'], message,
                       {'type': 'OTS', 'shape': out_shape})
        def _newComp(**init_args):
            return comp(**init_args)
        exec('self.%s = newComp' % name)

    # ------------------------------------ Convolution ------------------------------------ #

    def _getInitializer(self, initializer, param, regularizer):
        init_err = Exception('NEBULAE ERROR ⨷ %s initializer is not defined or supported.' % initializer)
        if initializer == 'xavier':
            if param is None:
                param = 'gaussian'
            else:
                if param=='normal':
                    param = 'gaussian'
                elif param!='uniform':
                    raise Exception('NEBULAE ERROR ⨷ %s-%s initializer is not defined or supported.' % (initializer, param))
            var = init.Xavier(param)
        elif initializer == 'uniform':
            if param is None:
                param = 0.5
            else:
                if param[0] != 0:
                    raise Exception('NEBULAE ERROR ⨷ the uniform distribution must be symmetric about y-axis in MXNet core.')
                param = param[1]
            var = init.Uniform(param)
        elif initializer == 'normal':
            if param is None:
                param = 0.1
            else:
                if param[0] != 0:
                    raise Exception('NEBULAE ERROR ⨷ the normal distribution must be zero-mean in MXNet core.')
                param = param[1]
            var = init.Normal(param)
        elif initializer == 'zero':
            var = init.Zero()
        elif initializer == 'one':
            var = init.One()
        else:
            raise init_err

        if regularizer == 'l2':
            pass
        else:
            raise Exception('NEBULAE ERROR ⨷ %s regularizer is not defined or supported.' % regularizer)

        return var

    def conv(self, **kwargs):
        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._conv, **kwargs), ['inputs'], kwargs['name'], [message],
                   {'type': 'CONV', 'cmajor': self.channel_major, 'out_chs': kwargs.get('out_chs', None),
                    'kernel': kwargs.get('kernel', None), 'stride': kwargs.get('stride', (1, 1)),
                    'auto_pad': kwargs.get('auto_pad', True)})
    def _conv(self, name, inputs, out_chs, kernel, w_init='xavier', w_param=None, b_init=None, b_param=None,
                w_reg='l2', b_reg='l2', stride=(1, 1), dilation=(1, 1), group=1, auto_pad=True):
        dim = len(kernel)
        if dim == 1:
            conv_func = nn.Conv1D
            if self.channel_major:
                dform = 'NCW'
            else:
                dform = 'NWC'
        elif dim == 2:
            conv_func = nn.Conv2D
            if self.channel_major:
                dform = 'NCHW'
            else:
                dform = 'NHWC'
        elif dim == 3:
            conv_func = nn.Conv3D
            if self.channel_major:
                dform = 'NCDHW'
            else:
                dform = 'NDHWC'
        else:
            raise Exception('NEBULAE ERROR ⨷ %d-d convolution is not supported.' % dim)

        if self.channel_major:
            size = inputs[2:]
        else:
            size = inputs[1:-1]
        if auto_pad:
            padding = []
            for d in range(dim):
                padding.append(ceil(((ceil(size[d] / stride[d]) - 1) * stride[d] + kernel[d] + (dilation[d] - 1) * (kernel[d] - 1) - size[d]) / 2))
        else:
            padding = dim * [0]
        if not w_init is None:
            w_init = self._getInitializer(w_init, w_param, w_reg)
        if not b_init is None:
            use_bias = True
            b_init = self._getInitializer(b_init, b_param, b_reg)
        else:
            use_bias = False
        return conv_func(channels=out_chs, kernel_size=kernel, strides=stride, padding=padding, dilation=dilation,
                         groups=group, layout=dform, use_bias=use_bias, weight_initializer=w_init, bias_initializer=b_init)

    def trans_conv(self, **kwargs):
        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._trans_conv, **kwargs), ['inputs'], kwargs['name'], [message],
                   {'type': 'CONV', 'cmajor': self.channel_major, 'out_chs': kwargs.get('out_chs', None),
                    'kernel': kwargs.get('kernel', None), 'stride': kwargs.get('stride', (1, 1)),
                    'auto_pad': kwargs.get('auto_pad', True)})
    def _trans_conv(self, name, inputs, output, kernel, w_init='xavier', w_param=None, b_init=None, b_param=None,
                w_reg='l2', b_reg='l2', stride=(1, 1), dilation=(1, 1), group=1, auto_pad=True):
        dim = len(kernel)
        if dim == 1:
            conv_func = nn.Conv1DTranspose
            if self.channel_major:
                dform = 'NCW'
            else:
                dform = 'NWC'
        elif dim == 2:
            conv_func = nn.Conv2DTranspose
            if self.channel_major:
                dform = 'NCHW'
            else:
                dform = 'NHWC'
        elif dim == 3:
            conv_func = nn.Conv3DTranspose
            if self.channel_major:
                dform = 'NCDHW'
            else:
                dform = 'NDHWC'
        else:
            raise Exception('NEBULAE ERROR ⨷ %d-d convolution is not supported.' % dim)

        if self.channel_major:
            in_size = inputs[2:]
            in_chs = inputs[1]
            out_chs = output[1]
            out_size = output[2:]
        else:
            in_size = inputs[1:-1]
            in_chs = inputs[-1]
            out_chs = output[-1]
            out_size = output[1:-1]
        if auto_pad:
            padding = []
            for d in range(dim):
                padding.append(ceil(((ceil(out_size[d] / stride[d]) - 1) * stride[d] + kernel[d] + (dilation[d] - 1)
                                     * (kernel[d] - 1) - out_size[d]) / 2))
        else:
            padding = dim * [0]
        compensation = []
        for d in range(dim):
            compensation.append(out_size[d] + 2 * padding[d] - kernel[d] - (in_size[d] - 1) * stride[d])
        if not w_init is None:
            w_init = self._getInitializer(w_init, w_param, w_reg)
        if not b_init is None:
            use_bias = True
            b_init = self._getInitializer(b_init, b_param, b_reg)
        else:
            use_bias = False
        return conv_func(out_chs, kernel, stride, padding, output_padding=compensation,
                         dilation=dilation, groups=group, layout=dform, use_bias=use_bias,
                         weight_initializer=w_init, bias_initializer=b_init, in_channels=in_chs)

    # ------------------------------------ Activation ------------------------------------ #

    def sigmoid(self, **kwargs):
        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._sigmoid, **kwargs), ['inputs'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _sigmoid(self, name, inputs):
        return MXsigmoid()

    def tanh(self, **kwargs):
        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._tanh, **kwargs), ['inputs'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _tanh(self, name, inputs):
        return MXtanh()

    def softmax(self, **kwargs):
        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._tanh, **kwargs), ['inputs'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _softmax(self, name, inputs):
        return MXsoftmax()

    def relu(self, **kwargs):
        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._relu, **kwargs), ['inputs'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _relu(self, name, inputs):
        return MXrelu()

    def relu_leaky(self, **kwargs):
        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._relu_leaky, **kwargs), ['inputs'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _relu_leaky(self, name, inputs, alpha=0.2):
        return nn.LeakyReLU(alpha)

    # ------------------------------------ Distributing ------------------------------------ #

    def dropout(self, **kwargs):
        message = []
        message.append(kwargs.get('inputs', '_INPUTS'))
        message.append(kwargs.get('is_train', '_IS_TRAIN'))
        return Pod(partial(self._dropout, **kwargs), ['inputs', 'is_train'], kwargs['name'], message, {'type': 'DROP'})
    def _dropout(self, name, inputs, p_drop, is_train):
        return nn.Dropout(p_drop)

    def batch_norm(self, **kwargs):
        message = []
        message.append(kwargs.get('inputs', '_INPUTS'))
        message.append(kwargs.get('is_train', '_IS_TRAIN'))
        return Pod(partial(self._batch_norm, **kwargs), ['inputs', 'is_train'], kwargs['name'], message,
                   {'type': 'BN', 'cmajor': self.channel_major})
    def _batch_norm(self, name, inputs, is_train, mmnt=0.9, beta=False, gamma=False):
        if self.channel_major:
            axis = 1
        else:
            axis = -1
        return nn.BatchNorm(axis=axis, momentum=mmnt, epsilon=1e-5, center=beta, scale=gamma)

    # def embedding(self, **kwargs):
    #     message = kwargs.get('inputs', '_INPUTS')
    #     return Pod(partial(self._embedding, **kwargs), ['inputs'], kwargs['name'], [message])
    # def _embedding(self, name, inputs, vocabulary, vec_dims, w_init='xavier', w_param=None):
    #     embd_vec = self._createVar(name+'_vec', [vocabulary, vec_dims], w_init, w_param)
    #     return tf.nn.embedding_lookup(embd_vec, inputs, name=name)

    # ------------------------------------ Pooling ------------------------------------ #

    def max_pool(self, **kwargs):
        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._max_pool, **kwargs), ['inputs'], kwargs['name'], [message],
                   {'type': 'POOL', 'cmajor': self.channel_major, 'kernel': kwargs.get('kernel', (2, 2)),
                    'stride': kwargs.get('stride', (2, 2)), 'auto_pad': kwargs.get('auto_pad', True),
                    'if_global': kwargs.get('if_global', False)})
    def _max_pool(self, name, inputs, kernel=(2, 2), stride=(2, 2), auto_pad=True, if_global=False):
        dim = len(kernel)
        if dim == 1:
            pool_func = nn.MaxPool1D
            if self.channel_major:
                dform = 'NCW'
            else:
                dform = 'NWC'
        elif dim == 2:
            pool_func = nn.MaxPool2D
            if self.channel_major:
                dform = 'NCHW'
            else:
                dform = 'NHWC'
        elif dim == 3:
            pool_func = nn.MaxPool3D
            if self.channel_major:
                dform = 'NCDHW'
            else:
                dform = 'NDHWC'
        else:
            raise Exception('NEBULAE ERROR ⨷ %d-d convolution is not supported.' % dim)

        if self.channel_major:
            size = inputs[2:]
        else:
            size = inputs[1:-1]
        if if_global:
            kernel = size
            if isinstance(kernel, int):
                kernel = (kernel,)
            padding = dim * [0]
            stride = dim * [1]
        else:
            if auto_pad:
                padding = []
                for d in range(dim):
                    padding.append(ceil(((ceil(size[d] / stride[d]) - 1) * stride[d] + kernel[d] - size[d]) / 2))
            else:
                padding = dim * [0]
        return pool_func(pool_size=kernel, strides=stride, padding=padding, ceil_mode=True, layout=dform)

    def avg_pool(self, **kwargs):
        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._avg_pool, **kwargs), ['inputs'], kwargs['name'], [message],
                   {'type': 'POOL', 'cmajor': self.channel_major, 'kernel': kwargs.get('kernel', (2, 2)),
                    'stride': kwargs.get('stride', (2, 2)), 'auto_pad': kwargs.get('auto_pad', True),
                    'if_global': kwargs.get('if_global', False)})
    def _avg_pool(self, name, inputs, kernel=(2, 2), stride=(2, 2), auto_pad=True, if_global=False):
        dim = len(kernel)
        if dim == 1:
            pool_func = nn.AvgPool1D
            if self.channel_major:
                dform = 'NCW'
            else:
                dform = 'NWC'
        elif dim == 2:
            pool_func = nn.AvgPool2D
            if self.channel_major:
                dform = 'NCHW'
            else:
                dform = 'NHWC'
        elif dim == 3:
            pool_func = nn.AvgPool3D
            if self.channel_major:
                dform = 'NCDHW'
            else:
                dform = 'NDHWC'
        else:
            raise Exception('NEBULAE ERROR ⨷ %d-d convolution is not supported.' % dim)

        if self.channel_major:
            size = inputs[2:]
        else:
            size = inputs[1:-1]
        if if_global:
            kernel = size
            padding = dim * [0]
            stride = dim * [1]
        else:
            if auto_pad:
                padding = []
                for d in range(dim):
                    padding.append(ceil(((ceil(size[d] / stride[d]) - 1) * stride[d] + kernel[d] - size[d]) / 2))
            else:
                padding = dim * [0]
        return pool_func(pool_size=kernel, strides=stride, padding=padding, ceil_mode=True, layout=dform)

    # ------------------------------------ Reshape ------------------------------------ #

    def reshape(self, **kwargs):
        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._reshape, **kwargs), ['inputs'], kwargs['name'], [message],
                   {'type': 'RESHAPE', 'shape': kwargs.get('shape', None)})
    def _reshape(self, name, inputs, shape):
        return MXreshape(*shape)
    #
    def flat(self, **kwargs):
        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._flat, **kwargs), ['inputs'], kwargs['name'], [message], {'type': 'FLAT'})
    def _flat(self, name, inputs):
        return nn.Flatten()
    #
    # def slice(self, **kwargs):
    #     message = kwargs.get('inputs', '_INPUTS')
    #     return Pod(partial(self._slice, **kwargs), ['inputs'], kwargs['name'], [message])
    # def _slice(self, name, inputs, indices):
    #     for d in range(len(indices)):
    #         output = inputs[indices[d][0]:indices[d][1]]
    #     return tf.identity(output, name)
    #
    # def pad(self, **kwargs):
    #     message = kwargs.get('inputs', '_INPUTS')
    #     return Pod(partial(self._pad, **kwargs), ['inputs'], kwargs['name'], [message])
    # def _pad(self, name, inputs, margin, fill_in=0):
    #     return tf.pad(inputs, margin, constant_values=fill_in, name=name)
    #
    # # -------------------------------------- Arithmetic -------------------------------------- #
    #
    # def clip(self, **kwargs):
    #     message = kwargs.get('inputs', '_INPUTS')
    #     return Pod(partial(self._clip, **kwargs), ['inputs'], kwargs['name'], [message])
    # def _clip(self, name, inputs, min_max_vals):
    #     return tf.clip_by_value(inputs, min_max_vals[0], min_max_vals[1], name)

    def dense(self, **kwargs):
        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._dense, **kwargs), ['inputs'], kwargs['name'], [message],
                   {'type': 'DENSE', 'out_chs': kwargs.get('out_chs', None), 'axis': kwargs.get('axis', -1)})
    def _dense(self, name, inputs, out_chs, axis=-1, w_init='xavier', w_param=None,
               b_init='zero', b_param=None, w_reg='l2', b_reg='l2'):
        if axis == 0:
            raise Exception('NEBULAE ERROR ⨷ you cannot apply dense layer along batch axis.')
        elif axis == -1:
            in_shape = None
            out_shape = None
        else:
            size = list(inputs)
            channel = (size[axis],)
            del size[axis]
            size[0] = -1
            in_shape = tuple(size) + channel
            out_shape = list(inputs)
            out_shape[0] = -1
            out_shape[axis] = out_chs
            out_shape = tuple(out_shape)

        if not w_init is None:
            w_init = self._getInitializer(w_init, w_param, w_reg)
        if not b_init is None:
            use_bias = True
            b_init = self._getInitializer(b_init, b_param, b_reg)
        else:
            use_bias = False
        return MXdense(out_chs, use_bias, w_init, b_init, in_shape, out_shape)

    # def argmax(self, **kwargs):
    #     message = kwargs.get('inputs', '_INPUTS')
    #     return Pod(partial(self._argmax, **kwargs), ['inputs'], kwargs['name'], [message])
    # def _argmax(self, name, inputs, axis):
    #     return tf.argmax(inputs, axis, name=name)
    #

    # ---------------------------------------- Wrapped Net ---------------------------------------- #



    # # ------------------------------------ Image Manipulation ------------------------------------ #
    #
    # def resize(self, **kwargs):
    #     message = kwargs.get('inputs', '_INPUTS')
    #     return Pod(partial(self._resize, **kwargs), ['inputs'], kwargs['name'], [message])
    # def _resize(self, name, inputs, size, method='bilinear'):
    #     if method == 'bilinear':
    #         return tf.image.resize_bilinear(inputs, size, name=name)
    #     elif method == 'bicubic':
    #         return tf.image.resize_bicubic(inputs, size, name=name)
    #     elif method == 'crop':
    #         return tf.image.resize_image_with_crop_or_pad(inputs, size, name=name)
    #     else:
    #         raise KeyError('NEBULAE ERROR ⨷ %s is not a legal resize method.' % method)
    #
    #
    # # ------------------------------------ Redefine or Rename ------------------------------------ #
    #
    def duplicate(self, **kwargs):
        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._duplicate, **kwargs), ['inputs'], kwargs['name'], [message], {'type': 'DUP'})
    def _duplicate(self, name, inputs):
        return Duplicate()
    #
    # def convert(self, **kwargs):
    #     message = kwargs.get('inputs', '_INPUTS')
    #     return Pod(partial(self._convert, **kwargs), ['inputs'], kwargs['name'], [message])
    # def _convert(self, name, inputs, dtype, trainable=False):
    #     '''
    #     convert data type or convert list/numpy array to tensor
    #     :param name:
    #     :param inputs: inputs tensor / list / numpy array
    #     :param dtype:
    #     :param trainable: if tensor is trainable
    #     :return: tensor
    #     '''
    #     if isinstance(inputs, (tf.Tensor, tf.SparseTensor, tf.Variable)):
    #         return tf.cast(inputs, tf.as_dtype(dtype), name=name)
    #     else:
    #         return tf.Variable(inputs, trainable=trainable, name=name)

    # ------------------------------------ Loss ------------------------------------ #

    def weight_decay(self, **kwargs):
        return Pod(partial(self._weight_decay, **kwargs), ['penalty'], kwargs['name'],
                   [nd.ones((1)) * kwargs['penalty']], {'type': 'LOSS'})
    def _weight_decay(self, name, penalty, decay_scope=None):
        if not decay_scope is None:
            raise Exception('NEBULAE ERROR ⨷ weight decay cannot be manipulated explicitly in MXNet core.')
        return MXwd()

    def sigm_xentropy(self, **kwargs):
        message = []
        message.append(kwargs.get('inputs', '_INPUTS'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._sigm_xentropy, **kwargs), ['inputs', 'label'], kwargs['name'], message, {'type': 'LOSS'})
    def _sigm_xentropy(self, name, inputs, label):
        return MXsigmxe()

    def sftm_xentropy(self, **kwargs):
        message = []
        message.append(kwargs.get('inputs', '_INPUTS'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._sftm_xentropy, **kwargs), ['inputs', 'label'], kwargs['name'], message, {'type': 'LOSS'})
    def _sftm_xentropy(self, name, inputs, label, is_one_hot):
        return MXsftmxe(is_one_hot)

    def mse(self, **kwargs):
        message = []
        message.append(kwargs.get('inputs', '_INPUTS'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._mse, **kwargs), ['inputs', 'label'], kwargs['name'], message, {'type': 'LOSS'})
    def _mse(self, name, inputs, label):
        return MXmse()

    def mae(self, **kwargs):
        message = []
        message.append(kwargs.get('inputs', '_INPUTS'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._mae, **kwargs), ['inputs', 'label'], kwargs['name'], message, {'type': 'LOSS'})
    def _mae(self, name, inputs, label):
        return MXmae()

    # ------------------------------------ Optimizer ------------------------------------ #

    def _lrStrategy(self, lr, lr_decay, miles, param):
        if lr_decay == 'step':
            return lr_scheduler.FactorScheduler(step=miles, factor=param, base_lr=lr)
        elif lr_decay == 'poly':
            return lr_scheduler.PolyScheduler(max_update=miles, base_lr=lr, pwr=param)
        elif lr_decay == 'cosine':
            return lr_scheduler.CosineScheduler(miles, base_lr=lr, final_lr=0.001*lr)
        elif lr_decay == 'exp':
            pass  #return tf.train.piecewise_constant(mileage, [i*param for i in range(1, len(lr))], lr)
        elif lr_decay == 'wavy':
            return CyclicalSchedule(CosineAnnealingSchedule, min_lr=0.001*lr, max_lr=lr,
                             cycle_length=miles, cycle_length_decay=1, cycle_magnitude_decay=param)
        else:
            raise KeyError('NEBULAE ERROR ⨷ %s decay is not supported or defined.' % lr_decay)

    def _selectParam(self, global_var, update_scope, ignore_name):
        update_var = ParameterDict()
        if ignore_name is None:
            ignore_name = []
        for l, p in global_var.items():
            if (update_scope is None or l.startswith(update_scope)) and (l not in ignore_name):
                update_var.update(p)
        return update_var

    def momentum(self, **kwargs):
        recargs = {k: v for k, v in kwargs.items() if k not in ('name', 'inputs', 'media')}
        recordConfig(os.path.join(os.getcwd(), 'nebulae_temp_config.json'),
                     recargs, overwrite=False)

        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._momentum, **kwargs), ['inputs', 'media'], kwargs['name'], [message, '_MEDIA'], {'type': 'OPTZ'})
    def _momentum(self, name, lr, inputs=None, mmnt=0.9, update_scope=None, ignore_name=None,
                  lr_decay=None, lr_miles=None, decay_param=None, grad_limit=None, media=None):
        # N.B. media is network and wd factor
        mod_params, wd = media
        wd = wd.asscalar()
        if isinstance(lr_decay, str):
            lr_s = self._lrStrategy(lr, lr_decay, lr_miles, decay_param)
        else:
            lr_s = lr_scheduler.LRScheduler(base_lr=lr)
        update_params = self._selectParam(mod_params, update_scope, ignore_name)
        optz = Trainer(update_params, 'SGD',
                       {'learning_rate': lr, 'momentum': mmnt, 'wd': wd,
                        'lr_scheduler': lr_s, 'clip_gradient': grad_limit})
        return optz

    def nesterov(self, **kwargs):
        recargs = {k: v for k, v in kwargs.items() if k not in ('name', 'inputs', 'media')}
        recordConfig(os.path.join(os.getcwd(), 'nebulae_temp_config.json'),
                     recargs, overwrite=False)

        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._nesterov, **kwargs), ['inputs', 'media'], kwargs['name'], [message, '_MEDIA'], {'type': 'OPTZ'})
    def _nesterov(self, name, lr, inputs=None, mmnt=0.9, update_scope=None, ignore_name=None,
                  lr_decay=None, lr_miles=None, decay_param=None, grad_limit=None, media=None):
        # N.B. media is network and wd factor
        mod_params, wd = media
        wd = wd.asscalar()
        if isinstance(lr_decay, str):
            lr_s = self._lrStrategy(lr, lr_decay, lr_miles, decay_param)
        else:
            lr_s = lr_scheduler.LRScheduler(base_lr=lr)
        update_params = self._selectParam(mod_params, update_scope, ignore_name)
        optz = Trainer(update_params, 'NAG',
                       {'learning_rate': lr, 'momentum': mmnt, 'wd': wd,
                        'lr_scheduler': lr_s, 'clip_gradient': grad_limit})
        return optz

    def adam(self, **kwargs):
        recargs = {k: v for k, v in kwargs.items() if k not in ('name', 'inputs', 'media')}
        recordConfig(os.path.join(os.getcwd(), 'nebulae_temp_config.json'),
                     recargs, overwrite=False)

        message = kwargs.get('inputs', '_INPUTS')
        return Pod(partial(self._adam, **kwargs), ['inputs', 'media'], kwargs['name'], [message, '_MEDIA'], {'type': 'OPTZ'})
    def _adam(self, name, lr, inputs=None, mmnt1=0.9, mmnt2=0.999, update_scope=None, ignore_name=None,
                  lr_decay=None, lr_miles=None, decay_param=None, grad_limit=None, media=None):
        # N.B. media is network and wd factor
        mod_params, wd = media
        wd = wd.asscalar()
        if isinstance(lr_decay, str):
            lr_s = self._lrStrategy(lr, lr_decay, lr_miles, decay_param)
        else:
            lr_s = lr_scheduler.LRScheduler(base_lr=lr)
        update_params = self._selectParam(mod_params, update_scope, ignore_name)
        optz = Trainer(update_params, 'Adam',
                       {'learning_rate': lr, 'beta1': mmnt1, 'beta2': mmnt2, 'wd': wd,
                        'lr_scheduler': lr_s, 'clip_gradient': grad_limit})
        return optz

    # ------------------------------------ Metric ------------------------------------ #

    def accuracy_cls(self, **kwargs):
        message = []
        message.append(kwargs.get('inputs', '_INPUTS'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._accuracy_cls, **kwargs), ['inputs', 'label'], kwargs['name'], message, {'type': 'ACC'})
    def _accuracy_cls(self, name, inputs, label, multi_class=False, is_one_hot=False):
        return AccuracyCLS(multi_class, is_one_hot)