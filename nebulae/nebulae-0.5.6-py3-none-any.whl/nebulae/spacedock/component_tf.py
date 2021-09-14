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
import tensorflow as tf
import os
from ..toolkit.utility import recordConfig
from .component import Pod

class ComponentTF(object):
    def __init__(self, channel_major=True, time_major=False):
        self.channel_major = channel_major
        self.time_major = time_major
        self.warehouse = ['CONV_1D', 'CONV', 'CONV_3D', 'CONV_TRANS', 'CONV_SEP',
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
        self.ERELU = 15
        # Pooling
        self.MAX_POOL = self.max_pool
        self.AVG_POOL = self.avg_pool
        # Distributing
        self.DROPOUT = self.dropout
        self.BATCH_NORM = self.batch_norm
        self.EMBEDDING = self.embedding
        # Reshape
        self.RESHAPE = self.reshape
        self.FLAT = self.flat
        self.SLICE = self.slice
        self.PAD = self.pad
        # Arithmetic
        self.CLIP = self.clip
        self.DENSE = self.dense
        self.ARGMAX = self.argmax
        # Image Manipulation
        self.RESIZE = self.resize
        # Copy or Rename
        self.DUPLICATE = self.duplicate
        self.CONVERT = self.convert
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

    def _createVar(self, name, shape, initializer, param, regularizer=None):
        init_err = Exception('NEBULAE ERROR ⨷ %s initializer is not defined or supported.' % initializer)
        # with tf.device('/gpu:0'):
        if initializer == 'xavier':
            if param=='normal':
                param = False
            elif param=='uniform':
                param = True
            else:
                param = False
            var = tf.get_variable(name, shape, initializer=tf.contrib.layers.xavier_initializer(uniform=param))
        elif initializer == 'uniform':
            if param is None:
                param = [-0.5, 0.5]
            var = tf.get_variable(name,
                                  initializer=tf.random_uniform(shape, minval=param[0], maxval=param[1]))
        elif initializer == 'normal':
            if param is None:
                param = [0, 0.1]
            var = tf.get_variable(name,
                                  initializer=tf.random_normal(shape, mean=param[0], stddev=param[1]))
        elif initializer == 'zero':
            var = tf.get_variable(name, shape, initializer=tf.zeros_initializer())
        elif initializer == 'one':
            var = tf.get_variable(name, shape, initializer=tf.ones_initializer())
        else:
            raise init_err

        if regularizer == 'l2':
            weight_decay = tf.nn.l2_loss(var, name=name+'/regularizer')
            tf.add_to_collection(tf.GraphKeys.REGULARIZATION_LOSSES, weight_decay)
        elif regularizer is None:
            pass
        else:
            raise Exception('NEBULAE ERROR ⨷ %s regularizer is not defined or supported.' % regularizer)

        return var

    def conv(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._conv, **kwargs), ['input'], kwargs['name'], [message], {'type': 'CONV'})
    # TODO: implement group convolution in tf
    def _conv(self, name, input, out_chs, kernel, w_init='xavier', w_param=None, b_init=None, b_param=None,
                w_reg='l2', b_reg='l2', stride=(1, 1), dilation=(1, 1), group=1, auto_pad=True):
        if auto_pad:
            padding = 'SAME'
        else:
            padding = 'VALID'
        if self.channel_major:
            in_chs = int(input.get_shape()[1])
        else:
            in_chs = int(input.get_shape()[-1])
        in_out_chs = (in_chs, out_chs)
        w = self._createVar(name+'_w', kernel + in_out_chs, w_init, w_param, w_reg)
        dim = len(kernel)
        if dim == 1:
            conv_func = tf.nn.conv1d
            if self.channel_major:
                dform = 'NCHW'
                stride = [1, 1] + list(stride)
                dilation = [1, 1] + list(dilation)
            else:
                dform = 'NHWC'
                stride = [1] + list(stride) + [1]
                dilation = [1] + list(dilation) + [1]
        elif dim == 2:
            conv_func = tf.nn.conv2d
            if self.channel_major:
                dform = 'NCHW'
                stride = [1, 1] + list(stride)
                dilation = [1, 1] + list(dilation)
            else:
                dform = 'NHWC'
                stride = [1] + list(stride) + [1]
                dilation = [1] + list(dilation) + [1]
        elif dim == 3:
            conv_func = tf.nn.conv3d
            if self.channel_major:
                dform = 'NCDHW'
                stride = [1, 1] + list(stride)
                dilation = [1, 1] + list(dilation)
            else:
                dform = 'NDHWC'
                stride = [1] + list(stride) + [1]
                dilation = [1] + list(dilation) + [1]
        else:
            raise Exception('NEBULAE ERROR ⨷ %d-d convolution is not supported.' % dim)
        if b_init:
            b = self._createVar(name+'_b', [in_out_chs[-1]], b_init, b_param, b_reg)
            if dim == 1:
                return tf.nn.bias_add(
                        conv_func(input, w, stride, padding, data_format=dform),
                        b, data_format=dform, name=name)
            else:
                return tf.nn.bias_add(
                        conv_func(input, w, stride, padding, dilations=dilation, data_format=dform),
                        b, data_format=dform, name=name)
        else:
            if dim == 1:
                return conv_func(input, w, stride, padding, data_format=dform, name=name)
            else:
                return conv_func(input, w, stride, padding, dilations=dilation, data_format=dform, name=name)

    # def trans_conv(self, **kwargs):
    #     message = kwargs.get('input', '_INPUT')
    #     return Pod(partial(self._trans_conv, **kwargs), ['input'], kwargs['name'], [message], {'type': 'TCONV'})
    # def _trans_conv(self, name, input, expected_out, kernel, w_init='xavier', w_param=None, b_init=None, b_param=None,
    #           w_reg='l2', b_reg='l2', stride=(1, 1), dilation=(1, 1), group=1, auto_pad=True):
    #     if auto_pad:
    #         padding = 'SAME'
    #     else:
    #         padding = 'VALID'
    #     if self.channel_major:
    #         in_chs = int(input.get_shape()[1])
    #     else:
    #         in_chs = int(input.get_shape()[-1])
    #     in_out_chs = (out_chs, in_chs)
    #     w = self._createVar(name + '_w', kernel + in_out_chs, w_init, w_param, w_reg)
    #     dim = len(kernel)
    #     if dim == 1:
    #         conv_func = tf.nn.conv1d
    #         if self.channel_major:
    #             dform = 'NCHW'
    #             stride = [1, 1] + list(stride)
    #             dilation = [1, 1] + list(dilation)
    #         else:
    #             dform = 'NHWC'
    #             stride = [1] + list(stride) + [1]
    #             dilation = [1] + list(dilation) + [1]
    #     elif dim == 2:
    #         conv_func = tf.nn.conv2d
    #         if self.channel_major:
    #             dform = 'NCHW'
    #             stride = [1, 1] + list(stride)
    #             dilation = [1, 1] + list(dilation)
    #         else:
    #             dform = 'NHWC'
    #             stride = [1] + list(stride) + [1]
    #             dilation = [1] + list(dilation) + [1]
    #     elif dim == 3:
    #         conv_func = tf.nn.conv3d
    #         if self.channel_major:
    #             dform = 'NCDHW'
    #             stride = [1, 1] + list(stride)
    #             dilation = [1, 1] + list(dilation)
    #         else:
    #             dform = 'NDHWC'
    #             stride = [1] + list(stride) + [1]
    #             dilation = [1] + list(dilation) + [1]
    #     else:
    #         raise Exception('NEBULAE ERROR ⨷ %d-d convolution is not supported.' % dim)
    #     if b_init:
    #         b = self._createVar(name + '_b', [in_out_chs[-2]], b_init, b_param, b_reg)
    #         if dim == 1:
    #             return tf.nn.bias_add(
    #                 conv_func(input, w, stride, padding, data_format=dform),
    #                 b, data_format=dform, name=name)
    #         else:
    #             return tf.nn.bias_add(
    #                 conv_func(input, w, stride, padding, dilations=dilation, data_format=dform),
    #                 b, data_format=dform, name=name)
    #     else:
    #         if dim == 1:
    #             return conv_func(input, w, stride, padding, data_format=dform, name=name)
    #         else:
    #             return conv_func(input, w, stride, padding, dilations=dilation, data_format=dform, name=name)

    # ------------------------------------ Activation ------------------------------------ #

    def sigmoid(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._sigmoid, **kwargs), ['input'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _sigmoid(self, name, input):
        return tf.nn.sigmoid(input, name)

    def tanh(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._tanh, **kwargs), ['input'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _tanh(self, name, input):
        return tf.nn.tanh(input, name)

    def softmax(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._tanh, **kwargs), ['input'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _softmax(self, name, input):
        return tf.nn.softmax(input, name)

    def relu(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._relu, **kwargs), ['input'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _relu(self, name, input):
        return tf.nn.relu(input, name)

    def relu_leaky(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._relu_leaky, **kwargs), ['input'], kwargs['name'], [message], {'type': 'ACTIVATION'})
    def _relu_leaky(self, name, input, alpha=0.2):
        return tf.nn.leaky_relu(input, alpha, name)

    # ------------------------------------ Distributing ------------------------------------ #

    def dropout(self, **kwargs):
        message = []
        message.append(kwargs.get('input', '_INPUT'))
        message.append(kwargs.get('is_train', '_IS_TRAIN'))
        return Pod(partial(self._dropout, **kwargs), ['input', 'is_train'], kwargs['name'], message, {'type': 'DROP'})
    def _dropout(self, name, input, p_drop, is_train):
        if is_train:
            p_keep = 1-p_drop
        else:
            p_keep = 1
        return tf.nn.dropout(input, p_keep)

    def batch_norm(self, **kwargs):
        message = []
        message.append(kwargs.get('input', '_INPUT'))
        message.append(kwargs.get('is_train', '_IS_TRAIN'))
        return Pod(partial(self._batch_norm, **kwargs), ['input', 'is_train'], kwargs['name'], message, {'type': 'BN'})
    def _batch_norm(self, name, input, is_train, beta=False, gamma=False):
        if self.channel_major:
            axis = 1
        else:
            axis = -1
        return tf.layers.batch_normalization(input, training=is_train, center=beta, scale=gamma, axis=axis, name=name)

    def embedding(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._embedding, **kwargs), ['input'], kwargs['name'], [message], {'type': 'EMBED'})
    def _embedding(self, name, input, vocabulary, vec_dims, w_init='xavier', w_param=None):
        embd_vec = self._createVar(name+'_vec', [vocabulary, vec_dims], w_init, w_param)
        return tf.nn.embedding_lookup(embd_vec, input, name=name)

    # ------------------------------------ Pooling ------------------------------------ #

    def max_pool(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._max_pool, **kwargs), ['input'], kwargs['name'], [message], {'type': 'POOL'})
    def _max_pool(self, name, input, kernel=(2, 2), stride=(2, 2), auto_pad=True, if_global=False):
        if auto_pad:
            padding = 'SAME'
        else:
            padding = 'VALID'
        dim = len(kernel)
        if dim == 2:
            pool_func = tf.nn.max_pool
            if self.channel_major:
                dform = 'NCHW'
                kernel = [1, 1] + list(kernel)
                stride = [1, 1] + list(stride)
            else:
                dform = 'NHWC'
                kernel = [1] + list(kernel) + [1]
                stride = [1] + list(stride) + [1]
        elif dim == 3:
            pool_func = tf.nn.max_pool3d
            if self.channel_major:
                dform = 'NCDHW'
                kernel = [1, 1] + list(kernel)
                stride = [1, 1] + list(stride)
            else:
                dform = 'NDHWC'
                kernel = [1] + list(kernel) + [1]
                stride = [1] + list(stride) + [1]
        else:
            raise Exception('NEBULAE ERROR ⨷ %d-d pooling is not supported.' % dim)
        if if_global:
            in_shape = input.get_shape()
            if self.channel_major:
                kernel = [1, 1] + [int(in_shape[-d] for d in range(dim, 0, -1))]
            else:
                kernel = [1] + [int(in_shape[-d] for d in range(dim+1, 1, -1))] + [1]
        return pool_func(input, kernel, stride, padding, data_format=dform, name=name)

    def avg_pool(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._avg_pool, **kwargs), ['input'], kwargs['name'], [message], {'type': 'POOL'})
    def _avg_pool(self, name, input, kernel=(2, 2), stride=(2, 2), auto_pad=True, if_global=False):
        if auto_pad:
            padding = 'SAME'
        else:
            padding = 'VALID'
        dim = len(kernel)
        if dim == 2:
            pool_func = tf.nn.avg_pool
            if self.channel_major:
                dform = 'NCHW'
                kernel = [1, 1] + list(kernel)
                stride = [1, 1] + list(stride)
            else:
                dform = 'NHWC'
                kernel = [1] + list(kernel) + [1]
                stride = [1] + list(stride) + [1]
        elif dim == 3:
            pool_func = tf.nn.avg_pool3d
            if self.channel_major:
                dform = 'NCDHW'
                kernel = [1, 1] + list(kernel)
                stride = [1, 1] + list(stride)
            else:
                dform = 'NDHWC'
                kernel = [1] + list(kernel) + [1]
                stride = [1] + list(stride) + [1]
        else:
            raise Exception('NEBULAE ERROR ⨷ %d-d pooling is not supported.' % dim)
        if if_global:
            in_shape = input.get_shape()
            if self.channel_major:
                kernel = [1, 1] + [int(in_shape[-d] for d in range(dim, 0, -1))]
            else:
                kernel = [1] + [int(in_shape[-d] for d in range(dim + 1, 1, -1))] + [1]
        return pool_func(input, kernel, stride, padding, data_format=dform, name=name)

    # ------------------------------------ Reshape ------------------------------------ #

    def reshape(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._reshape, **kwargs), ['input'], kwargs['name'], [message], {'type': 'RESHAPE'})
    def _reshape(self, name, input, shape):
        return tf.reshape(input, shape, name)

    def flat(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._flat, **kwargs), ['input'], kwargs['name'], [message], {'type': 'FLAT'})
    def _flat(self, name, input):
        return tf.layers.flatten(input, name=name)

    def slice(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._slice, **kwargs), ['input'], kwargs['name'], [message], {'type': 'SLICE'})
    def _slice(self, name, input, indices):
        for d in range(len(indices)):
            output = input[indices[d][0]:indices[d][1]]
        return tf.identity(output, name)

    def pad(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._pad, **kwargs), ['input'], kwargs['name'], [message], {'type': 'PAD'})
    def _pad(self, name, input, margin, fill_in=0):
        return tf.pad(input, margin, constant_values=fill_in, name=name)

    # -------------------------------------- Arithmetic -------------------------------------- #

    def clip(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._clip, **kwargs), ['input'], kwargs['name'], [message], {'type': 'CLIP'})
    def _clip(self, name, input, min_max_vals):
        return tf.clip_by_value(input, min_max_vals[0], min_max_vals[1], name)

    def dense(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._dense, **kwargs), ['input'], kwargs['name'], [message], {'type': 'DENSE'})
    def _dense(self, name, input, out_chs, axis=-1, w_init='xavier', w_param=None,
               b_init='zero', b_param=None, w_reg='l2', b_reg='l2'):
        size = input.get_shape().as_list()
        in_chs = size[axis]
        in_out_chs = [in_chs, out_chs]
        if axis == 0:
            raise Exception('NEBULAE ERROR ⨷ you cannot apply dense layer along batch axis.')
        elif axis == -1:
            w = self._createVar(name + '_w', in_out_chs, w_init, w_param, w_reg)
            if b_init:
                b = self._createVar(name + '_b', [in_out_chs[-1]], b_init, b_param, b_reg)
                return tf.nn.bias_add(tf.matmul(input, w), b, name=name)
            else:
                return tf.matmul(input, w, name=name)
        else:
            channel = (in_chs,)
            del size[axis]
            size[0] = -1
            in_shape = tuple(size) + channel
            out_shape = list(input[0])
            out_shape[0] = -1
            out_shape[axis] = out_chs
            out_shape = tuple(out_shape)
            w = self._createVar(name + '_w', in_out_chs, w_init, w_param, w_reg)
            if b_init:
                b = self._createVar(name + '_b', [in_out_chs[-1]], b_init, b_param, b_reg)
                return tf.reshape(tf.nn.bias_add(tf.matmul(tf.reshape(input, in_shape), w), b), out_shape, name=name)
            else:
                return tf.reshape(tf.matmul(tf.reshape(input, in_shape), w), out_shape, name=name)

    def argmax(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._argmax, **kwargs), ['input'], kwargs['name'], [message], {'type': 'ARG'})
    def _argmax(self, name, input, axis):
        return tf.argmax(input, axis, name=name)

    # ------------------------------------ Image Manipulation ------------------------------------ #

    def resize(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._resize, **kwargs), ['input'], kwargs['name'], [message], {'type': 'RESHAPE'})
    def _resize(self, name, input, size, method='bilinear'):
        if method == 'bilinear':
            return tf.image.resize_bilinear(input, size, name=name)
        elif method == 'bicubic':
            return tf.image.resize_bicubic(input, size, name=name)
        elif method == 'crop':
            return tf.image.resize_image_with_crop_or_pad(input, size, name=name)
        else:
            raise KeyError('NEBULAE ERROR ⨷ %s is not a legal resize method.' % method)


    # ------------------------------------ Redefine or Rename ------------------------------------ #

    def duplicate(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._duplicate, **kwargs), ['input'], kwargs['name'], [message], {'type': 'DUP'})
    def _duplicate(self, name, input):
        return tf.identity(input, name)

    def convert(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._convert, **kwargs), ['input'], kwargs['name'], [message], {'type': 'CAST'})
    def _convert(self, name, input, dtype, trainable=False):
        '''
        convert data type or convert list/numpy array to tensor
        :param name:
        :param input: input tensor / list / numpy array
        :param dtype:
        :param trainable: if tensor is trainable
        :return: tensor
        '''
        if isinstance(input, (tf.Tensor, tf.SparseTensor, tf.Variable)):
            return tf.cast(input, tf.as_dtype(dtype), name=name)
        else:
            return tf.Variable(input, trainable=trainable, name=name)

    # ------------------------------------ Loss ------------------------------------ #

    def weight_decay(self, **kwargs):
        # message = kwargs.get('penalty', '.penalty')
        return Pod(partial(self._weight_decay, **kwargs), [], kwargs['name'], [], {'type': 'LOSS'})
    def _weight_decay(self, name, penalty, decay_scope=None):
        if decay_scope is None:
            return tf.multiply(tf.add_n(tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)),
                               penalty, name=name)
        else:
            return tf.multiply(tf.add_n(tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES, scope=decay_scope)),
                               penalty, name=name)

    def sigm_xentropy(self, **kwargs):
        message = []
        message.append(kwargs.get('input', '_INPUT'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._sigm_xentropy, **kwargs), ['input', 'label'], kwargs['name'], message, {'type': 'LOSS'})
    def _sigm_xentropy(self, name, input, label):
        labels = tf.cast(label, tf.float32)
        return tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=label, logits=input, name=name))

    def sftm_xentropy(self, **kwargs):
        message = []
        message.append(kwargs.get('input', '_INPUT'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._sftm_xentropy, **kwargs), ['input', 'label'], kwargs['name'], message, {'type': 'LOSS'})
    def _sftm_xentropy(self, name, input, label, is_one_hot):
        if is_one_hot:
            labels = tf.cast(label, tf.float32)
            return tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=labels, logits=input, name=name))
        else:
            return tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(
                                        labels=label, logits= input, name=name))

    def mse(self, **kwargs):
        message = []
        message.append(kwargs.get('input', '_INPUT'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._mse, **kwargs), ['input', 'label'], kwargs['name'], message, {'type': 'LOSS'})
    def _mse(self, name, input, label):
        return tf.reduce_mean(tf.squared_difference(input, label), name=name)

    def mae(self, **kwargs):
        message = []
        message.append(kwargs.get('input', '_INPUT'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._mae, **kwargs), ['input', 'label'], kwargs['name'], message, {'type': 'LOSS'})
    def _mae(self, name, input, label):
        return tf.reduce_mean(tf.abs(input-label), name=name)

    # ------------------------------------ Optimizer ------------------------------------ #

    def _lrStrategy(self, mileage, lr, lr_decay, miles, param):
        if lr_decay == 'step':
            return tf.train.exponential_decay(lr, mileage, miles, decay_rate=param, staircase=True)
        elif lr_decay == 'poly':
            return tf.train.polynomial_decay(lr, mileage, miles, power=param, cycle=False)
        elif lr_decay == 'cosine':
            return tf.train.cosine_decay(lr, mileage, miles, alpha=lr*0.001)
        elif lr_decay == 'exp':
            return tf.train.exponential_decay(lr, mileage, miles, decay_rate=param, staircase=False)
        elif lr_decay == 'wavy':
            return tf.train.cosine_decay_restarts(lr, mileage, miles, t_mul=1.0, m_mul=param, alpha=lr*0.001)
        else:
            raise KeyError('NEBULAE ERROR ⨷ %s decay is not supported or defined.' % lr_decay)

    def _computeGrad(self, optz, cost, update_scope, ignore_name, grad_limit):
        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(update_ops):
            if update_scope is None:
                tr_var = tf.trainable_variables()
            else:
                tr_var = tf.trainable_variables(scope=update_scope)
            if not ignore_name is None:
                update_var = []
                for tv in tr_var:
                    flag_ignore = False
                    for ig in ignore_name:
                        if ig in tv.op.name:
                            flag_ignore = True
                            break
                    if not flag_ignore:
                        update_var.append(tv)
            else:
                update_var = tr_var
            grad_var_pairs = optz.compute_gradients(cost, var_list=update_var)

            if grad_limit is None:
                return grad_var_pairs
            else:
                return [(tf.clip_by_value(grad, -grad_limit, grad_limit), var) for grad, var in grad_var_pairs]

    def momentum(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._momentum, **kwargs), ['input', 'media'], kwargs['name'], [message, '_MEDIA'], {'type': 'OPTZ'})
    def _momentum(self, name, input, lr, mmnt=0.9, update_scope=None, ignore_name=None,
                  lr_decay=None, lr_miles=None, decay_param=None, grad_limit=None, media=None):
        recordConfig(os.path.join(os.getcwd(), 'temp_config.json'),
                     {'lr': lr, 'mmnt': mmnt, 'update_scope': update_scope, 'ignore_name': ignore_name,
                      'lr_decay': lr_decay, 'lr_miles': lr_miles, 'decay_param': decay_param, 'grad_limit': grad_limit})
        if isinstance(lr_decay, str):
            lr = self._lrStrategy(media, lr, lr_decay, lr_miles, decay_param)
        optz = tf.train.MomentumOptimizer(lr, mmnt)
        grad = self._computeGrad(optz, input, update_scope, ignore_name, grad_limit)
        train_op = optz.apply_gradients(grad, media, name=name)
        return train_op

    def nesterov(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._nesterov, **kwargs), ['input', 'media'], kwargs['name'], [message, '_MEDIA'], {'type': 'OPTZ'})
    def _nesterov(self, name, input, lr, mmnt=0.9, update_scope=None, ignore_name=None,
                  lr_decay=None, lr_miles=None, decay_param=None, grad_limit=None, media=None):
        recordConfig(os.path.join(os.getcwd(), 'temp_config.json'),
                     {'lr': lr, 'mmnt': mmnt, 'update_scope': update_scope, 'ignore_name': ignore_name,
                      'lr_decay': lr_decay, 'lr_miles': lr_miles, 'decay_param': decay_param, 'grad_limit': grad_limit})
        if isinstance(lr_decay, str):
            lr = self._lrStrategy(media, lr, lr_decay, lr_miles, decay_param)
        optz = tf.train.MomentumOptimizer(lr, mmnt, use_nesterov=True)
        grad = self._computeGrad(optz, input, update_scope, ignore_name, grad_limit)
        train_op = optz.apply_gradients(grad, media, name=name)
        return train_op

    def adam(self, **kwargs):
        message = kwargs.get('input', '_INPUT')
        return Pod(partial(self._adam, **kwargs), ['input', 'media'], kwargs['name'], [message, '_MEDIA'], {'type': 'OPTZ'})
    def _adam(self, name, input, lr, mmnt1=0.9, mmnt2=0.999, update_scope=None, ignore_name=None,
                  lr_decay=None, lr_miles=None, decay_param=None, grad_limit=None, media=None):
        recordConfig(os.path.join(os.getcwd(), 'temp_config.json'),
                     {'lr': lr, 'mmnt1': mmnt1, 'mmnt2': mmnt2, 'update_scope': update_scope,
                      'ignore_name': ignore_name, 'lr_decay': lr_decay, 'lr_miles': lr_miles,
                      'decay_param': decay_param, 'grad_limit': grad_limit})
        if isinstance(lr_decay, str):
            lr = self._lrStrategy(media, lr, lr_decay, lr_miles, decay_param)
        optz = tf.train.AdamOptimizer(lr, beta1=mmnt1, beta2=mmnt2)
        grad = self._computeGrad(optz, input, update_scope, ignore_name, grad_limit)
        train_op = optz.apply_gradients(grad, media, name=name)
        return train_op

    # ------------------------------------ Metric ------------------------------------ #

    def accuracy_cls(self, **kwargs):
        message = []
        message.append(kwargs.get('input', '_INPUT'))
        message.append(kwargs.get('label', '_LABEL'))
        return Pod(partial(self._accuracy_cls, **kwargs), ['input', 'label'], kwargs['name'], message, {'type': 'ACC'})
    def _accuracy_cls(self, name, input, label, multi_class, is_one_hot=False):
        if multi_class:
            assert not is_one_hot
            pred = tf.cast(tf.round(input), label.dtype)
            correct = tf.reduce_all(tf.equal(pred, label), axis=-1)
            return tf.reduce_mean(tf.cast(correct, tf.float32), name=name)
        else:
            if is_one_hot:
                label = tf.argmax(label, axis=-1)
            pred = tf.argmax(input, axis=-1)
            correct = tf.equal(pred, label)
            return tf.reduce_mean(tf.cast(correct, tf.float32), name=name)