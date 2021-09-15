#!/usr/bin/env python
'''
space_craft_mx
Created by Seria at 06/02/2019 8:45 PM
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
from mxnet import nd
from mxnet import symbol as syb
from mxnet.gluon import nn, ParameterDict, HybridBlock
import numpy as np
from .component import Pod
from ..toolkit.utility import _ImperativeSymbol



class SpaceCraftMX(HybridBlock):
    def __init__(self, device, blueprint, scope='', lookup=None):
        assert '/' not in scope
        self.scope = scope
        prefix = scope if scope else None
        super(SpaceCraftMX, self).__init__(prefix=prefix)
        self.valid_dtypes = ['uint8', 'int8', 'int16', 'int32', 'int64',
                             'float16', 'float32', 'float64', 'str', 'bool']
        self.operands = {'+': nd.add, '-': nd.subtract, '*': nd.multiply, '@': nd.batch_dot, '&': nd.concat}
        self.operands_counter = {'+': 0, '-': 0, '*': 0, '@': 0, '&': 0}
        self.dict = {'_INPUTS': nd.zeros((1), ctx=device),
                       '_PENALTY': nd.zeros((1), ctx=device)}
        self.ID = set() # record all assembled components in layout
        self.flag_init = True
        self.debut = True
        self._launcher = {}
        self.terminator = {}
        self._parameters = {}
        self.module = []
        self.comp = []
        self.in_node = []
        self.out_node = []
        self._ImpSym = _ImperativeSymbol()
        self.device = device
        self.blueprint = blueprint
        self.lookup = lookup

    def hybrid_forward(self, F, *args):
        for i, k in enumerate(self.in_node):
            self.dict[k] = args[i]
        # reset
        self.operands_counter = {'+': 0, '-': 0, '*': 0, '@': 0, '&': 0}
        self.ID = set()
        # parse components
        for mod, scope in self.module:
            _ = self._assemble(mod, sub_scope=scope)
        # only once
        if self.flag_init:
            self.blueprint.log()
            self.blueprint.param['verbose'] = False
            # self.hybridize()
            self.flag_init = False
        output = {}
        for node in self.out_node:
            output[node] = self.dict[node]
        return output

    def __getitem__(self, key):
        value = self.dict[key]
        if value.size == 1:
            return value.asscalar()
        else:
            return value.asnumpy()

    def _getHull(self, comp_name):
        shape = self._ImpSym.tensors_out[comp_name]
        if len(shape)<1: # usually is a global flag
            return ' 1 '
        hull = ' ' + ' x '.join([str(size) for size in shape if size>0])
        return hull

    def _assemble(self, component, assemblage=None, sub_scope='', virtual=False):
        '''
        :param component:
        :param assemblage:
        :param sub_scope:
        :param virtual: if True, build up network architecture before hybridization
        :return:
        '''
        symbol = component.symbol
        message = component.message
        info = component.info
        if sub_scope:
            sub_prefix = sub_scope + '/'
        else:
            sub_prefix = sub_scope
        if symbol == '>':
            for comp in component.component:
                assemblage = self._assemble(comp, assemblage=assemblage, sub_scope=sub_scope, virtual=virtual)
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
                assemblage = self._assemble(comp, assemblage=init_assemblage, sub_scope=sub_scope, virtual=virtual)
                if virtual:
                    continue
                assemblage_list.append(assemblage)
                hull = self._getHull(assemblage)
                hull_list.append(hull)
                if operator is None:
                    operator = self.dict[assemblage]
                else:
                    # if not self.flag_init:
                    #     if symbol == '&':
                    #         operator = syb.concat([operator, self.dict[assemblage]], dim=-1)
                    #     elif symbol == '@':
                    #         operator = syb.batch_dot(operator, self.dict[assemblage])
                    #     elif symbol == '+':
                    #         operator = operator + self.dict[assemblage]
                    #     elif symbol == '-':
                    #         operator = operator - self.dict[assemblage]
                    #     elif symbol == '*':
                    #         operator = operator * self.dict[assemblage]
                    # else:
                    if symbol == '&':
                        operator = self.operands[symbol]([operator, self.dict[assemblage]], dim=-1)
                    else:
                        operator = self.operands[symbol](operator, self.dict[assemblage])
            asmb_full_name = sub_prefix + assemblage_name
            if virtual:
                return asmb_full_name
            self.dict[asmb_full_name] = operator
            self.ID.add(asmb_full_name)
            self.blueprint._combineNodes(assemblage_list, hull_list,
                                         asmb_full_name, symbol)
            return asmb_full_name
        else: # this is an atomic component
            # handle input from external SC
            for msg in message:
                if isinstance(msg, str) and ':' in msg:
                    sc, key = msg.split(':')
                    self.dict[msg] = self.lookup(sc)[key]
                    self._ImpSym.tensors_out[msg] = self.lookup(sc)._ImpSym.tensors_out[key]
            # get absolute name under SC
            node_name = sub_prefix + component.name
            # instantiate input arguments
            args = ()
            for s, sym in enumerate(symbol):
                if virtual:
                # special conditions
                    if sym == 'penalty':
                        self.dict['_PENALTY'] = message[s].as_in_context(self.device)
                        message[s] = '_PENALTY'
                    elif sym == 'is_train':
                        self.dict['_IS_TRAIN'] = message[s]
                    continue
                elif sym == 'is_train':
                    continue
                args += (self.dict[component.message[s]],)
            if virtual:
                self._parameters[node_name] = component.component.collect_params()
                return node_name
            if node_name in self.ID:  # Reuse or Redefine an existent node
                assert info['type'] == 'DUP' and len(message) == 1  # the only way to reuse is invoking DUPLICATE with single input
                hull_in = self._getHull(message[0])
                hull_out = self._getHull(node_name)
                self.blueprint._drawNode(message[0], node_name, hull_in, hull_out)
                return node_name
            if assemblage is None:
                self.dict[node_name] = component.component(*args)
                self.ID.add(node_name)
                if symbol[0] == 'penalty':
                    self.blueprint._drawNode(node_name, node_name, visible=False)
            else:
                if symbol[0] == 'penalty':
                    self.dict[node_name] = component.component(*args)
                    self.ID.add(node_name)
                    self.blueprint._drawNode(node_name, node_name, visible=False)
                else: # message includes input at least
                    args = (self.dict[assemblage],) + args[1:]
                    self.dict[node_name] = component.component(*args)
                    self.ID.add(node_name)
                    # draw layout sheet
                    hull_in = self._getHull(assemblage)
                    hull_out = self._getHull(node_name)
                    self.blueprint._drawNode(assemblage, node_name, hull_in, hull_out)
            for msg in message:
                # draw layout sheet
                if isinstance(msg, str) and msg[0]!='_':
                    hull_in = self._getHull(msg)
                    hull_out = self._getHull(node_name)
                    self.blueprint._drawNode(msg, node_name, hull_in, hull_out)
            return node_name

    def _finalize(self, first_call):
        if first_call:
            for c in self.comp:
                self.register_child(c)
            for k in self.terminator.keys():
                self.dict[k] = None
        else:
            if self.debut:
                self.initialize(ctx=self.device)
            for k in self.terminator.keys():
                self.dict[k] = self.terminator[k].component(media=(self._parameters, self.dict['_PENALTY']))

    def _allot(self, comp, sub_scope, is_optz):
        self._ImpSym.infer(comp, sub_scope=sub_scope)
        if is_optz: # is optimizer
            if sub_scope:
                assemblage = sub_scope + '/' + comp.name
            else:
                assemblage = comp.name
            self.terminator[assemblage] = comp
        else:
            self.module.append((comp, sub_scope))
            # complete input arguments of every component
            self.comp += self.module[-1][0]._build(self._ImpSym.tensors_in)
            assemblage = self._assemble(comp, sub_scope=sub_scope, virtual=True)
        return assemblage

    def slot(self, name, shape, dtype):
        if dtype not in self.valid_dtypes:
            raise Exception('NEBULAE ERROR ⨷ %s is not a valid data type.' % dtype)
        if dtype in ['float16', 'float32', 'float64', 'int32', 'int64', 'int8', 'uint8']:
            self.in_node.append(name)
        self._launcher[name] = (shape, dtype)
        self._ImpSym.enroll(name, shape)

    def assemble(self, component, sub_scope=''):
        if not isinstance(component, Pod):
            raise TypeError('NEBULAE ERROR ⨷ only the members in Component can be assembled.')
        optype = component._isOptz()
        if optype == 1:
            assemblage = self._allot(component, sub_scope, True)
        elif optype == -1:
            assemblage = self._allot(component, sub_scope, False)
        else:
            _ = self._allot(component.component[0], sub_scope, False)
            assemblage = self._allot(component.component[1], sub_scope, True)
        return assemblage