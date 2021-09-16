#!/usr/bin/env python
'''
space_craft_tf
Created by Seria at 03/02/2019 11:25 AM
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
import tensorflow as tf
import numpy as np
from .component import Pod


class SpaceCraftTF(object):
    def __init__(self, engine, blueprint, scope=''):
        assert '/' not in scope
        if scope:
            self.scope = scope + '/'
        else:
            self.scope = scope
        self.valid_dtypes = ['uint8', 'int8', 'int16', 'int32', 'int64',
                             'float16', 'float32', 'float64', 'str', 'bool']
        self.operands = {'+': tf.add, '-': tf.subtract, '*': tf.multiply, '@': tf.matmul, '&': tf.concat}
        self.operands_counter = {'+': 0, '-': 0, '*': 0, '@': 0, '&': 0}
        self.layout = {'_INPUT': tf.constant(0), '_MEDIA': tf.Variable(0, trainable=False)}
        self.engine = engine
        self.blueprint = blueprint

    def fillUp(self, name, shape, dtype):
        if dtype not in self.valid_dtypes:
            raise Exception('NEBULAE ERROR ⨷ %s is not a valid data type.' % dtype)
        self.layout[name] = tf.placeholder(tf.as_dtype(dtype), shape, name)

    def _getHull(self, component):
        component = self.layout[component]
        if isinstance(component, (tf.Tensor, tf.SparseTensor, tf.Variable)):
            tshape = component.get_shape()
            if tshape.dims is None or tshape.ndims == 0:
                return ' 1    '
            shape = tshape[1:].as_list()
        elif isinstance(component, np.ndarray):
            shape = list(component.shape)
        else:
            shape = [1]
        len_wo_bs = len(shape) - 1
        hull = ' '
        if len_wo_bs < 0:
            return ' 1    '
        for dim in range(len_wo_bs):
            hull += '%-4d x ' % shape[dim]
        hull += '%-5d' % shape[-1]
        return hull

    def _assemble(self, component, assemblage=None, sub_scope=''):
        symbol = component.symbol
        message = component.message
        if sub_scope:
            sub_prefix = sub_scope + '/'
        else:
            sub_prefix = sub_scope
        # this is an atomic component
        if symbol == '>':
            for comp in component.component:
                assemblage = self.assemble(comp, assemblage=assemblage,
                                           sub_scope=sub_scope, is_external=False)
            return assemblage
        elif symbol in ['+', '-', '*', '@', '&']:
            operator = None
            self.operands_counter[symbol] += 1
            # TODO: if a pod is extended to more than two comps, assemblage_name needs modification
            assemblage_name = component.name + '_' + str(self.operands_counter[symbol])
            assemblage_list = []
            hull_list = []
            init_assemblage = assemblage
            for comp in component.component:
                assemblage = self.assemble(comp, assemblage=init_assemblage,
                                           sub_scope=sub_scope, is_external=False)
                assemblage_list.append(assemblage)
                hull = self._getHull(assemblage)
                hull_list.append(hull)
                if operator is None:
                    operator = self.layout[assemblage]
                else:
                    if symbol == '&':
                        operator = self.operands[symbol]([operator, self.layout[assemblage]],
                                                              axis=-1, name=assemblage_name)
                    else:
                        operator = self.operands[symbol](operator,
                                                              self.layout[assemblage],
                                                              name=assemblage_name)
            asmb_full_name = sub_prefix + assemblage_name
            self.layout[asmb_full_name] = operator
            self.blueprint._combineNodes(assemblage_list, hull_list,
                                         asmb_full_name, symbol)
            return asmb_full_name
        else:
            node_name = sub_prefix + component.name
            if node_name in self.layout.keys():  # Reuse or Redefine an existent node
                assert len(message) == 1  # the only way to reuse is invoking DUPLICATE with single input
                hull = self._getHull(message[0])
                self.blueprint._drawNode(message[0], node_name, hull)
                return node_name
            # instantiate input arguments
            kwargs = {'name': node_name}
            for s, sym in enumerate(symbol):
                kwargs[sym] = self.layout[message[s]]

            if assemblage is None:
                self.layout[node_name] = component.component(**kwargs)
                if len(symbol) == 0:
                    self.blueprint._drawNode(node_name, node_name, visible=False)
            else:
                if len(symbol) == 0:
                    self.layout[node_name] = component.component(**kwargs)
                    self.blueprint._drawNode(node_name, node_name, visible=False)
                else:  # message includes input at least
                    kwargs['input'] = self.layout[assemblage]
                    self.layout[node_name] = component.component(**kwargs)
                    # draw layout sheet
                    hull = self._getHull(assemblage)
                    self.blueprint._drawNode(assemblage, node_name, hull)
            for msg in message:
                # draw layout sheet
                if msg[0]!='_' and isinstance(self.layout[msg], (tf.Tensor, tf.SparseTensor, tf.Variable)):
                    hull = self._getHull(msg)
                    self.blueprint._drawNode(msg, node_name, hull)
            return node_name

    def assemble(self, component, sub_scope='', assemblage=None, is_external=True):
        if not isinstance(component, Pod):
            raise TypeError('NEBULAE ERROR ⨷ only the members from Component can be assembled.')
        if not is_external:
            return self._assemble(component, assemblage=assemblage, sub_scope=sub_scope)
        else:
            # append sub scope
            if sub_scope:
                scope = self.scope + sub_scope + '/'
            else:
                scope = self.scope
            # whether to reuse variable name
            reuse = tf.AUTO_REUSE
            with tf.variable_scope(scope, reuse=reuse):
                return self._assemble(component, assemblage=assemblage, sub_scope=sub_scope)