#!/usr/bin/env python
'''
space_craft_pt
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
import torch
import torch.nn as nn
import numpy as np
from .component import Pod
from ..toolkit.utility import _ImperativeSymbol



def subtract(x, y):
    return torch.add(x, torch.neg(y))

class SpaceCraftPT(nn.Module):
    def __init__(self, engine, blueprint, scope=''):
        assert '/' not in scope
        if scope:
            self.scope = scope + '/'
        else:
            self.scope = scope
        super(SpaceCraftPT, self).__init__()
        self.valid_dtypes = ['uint8', 'int8', 'int16', 'int32', 'int64',
                             'float16', 'float32', 'float64', 'str', 'bool']
        self.operands = {'+': torch.add, '-': subtract, '*': torch.mul, '@': torch.bmm, '&': torch.cat}
        self.operands_counter = {'+': 0, '-': 0, '*': 0, '@': 0, '&': 0}
        self.layout = {'_INPUT': torch.zeros(1, device=self.engine.context),
                       '_PENALTY': torch.zeros(1, device=self.engine.context)}
        self.ID = set() # record all assembled components in layout
        self.flag_init = True
        self._launcher = {}
        self._parameters = {}
        self._states = {}
        self.terminator = {}
        self.module = []
        self.comp = []
        self.in_node = []
        self.out_node = []
        self._ImpSym = _ImperativeSymbol()
        self.engine = engine
        self.blueprint = blueprint

    def forward(self, *args):
        for i, k in enumerate(self.in_node):
            self.layout[k] = args[i]
        # reset
        self.operands_counter = {'+': 0, '-': 0, '*': 0, '@': 0, '&': 0}
        self.ID = set()
        # parse components
        for mod, scope in self.module:
            _ = self._assemble(mod, sub_scope=scope)
        # only once
        if self.flag_init:
            self.blueprint.log(None)
            self.blueprint.param['verbose'] = False
            self.flag_init = False
        output = {}
        for node in self.out_node:
            output[node] = self.layout[node]
        return output

    def _getHull(self, component):
        if component not in self.layout:
            shape = self._launcher[component][0]
        else:
            component = self.layout[component]
            if torch.is_tensor(component):
                shape = component.shape[1:]
            elif isinstance(component, np.ndarray):
                shape = list(component.shape)
            else:
                shape = [1]
        # length without batch size
        len_wo_bs = len(shape) - 1
        if len_wo_bs<0:
            return ' 1    '
        hull = ' '
        for dim in range(len_wo_bs):
            hull += '%-4d x ' % shape[dim]
        hull += '%-5d' % shape[-1]
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
                    operator = self.layout[assemblage]
                else:
                    # if not self.flag_init:
                    #     if symbol == '&':
                    #         operator = syb.concat([operator, self.layout[assemblage]], dim=-1)
                    #     elif symbol == '@':
                    #         operator = syb.batch_dot(operator, self.layout[assemblage])
                    #     elif symbol == '+':
                    #         operator = operator + self.layout[assemblage]
                    #     elif symbol == '-':
                    #         operator = operator - self.layout[assemblage]
                    #     elif symbol == '*':
                    #         operator = operator * self.layout[assemblage]
                    # else:
                    if symbol == '&':
                        operator = self.operands[symbol]([operator, self.layout[assemblage]], dim=-1)
                    else:
                        operator = self.operands[symbol](operator, self.layout[assemblage])
            asmb_full_name = sub_prefix + assemblage_name
            if virtual:
                return asmb_full_name
            self.layout[asmb_full_name] = operator
            self.ID.add(asmb_full_name)
            self.blueprint._combineNodes(assemblage_list, hull_list,
                                         asmb_full_name, symbol)
            return asmb_full_name
        else: # this is an atomic component
            node_name = sub_prefix + component.name
            # instantiate input arguments
            args = ()
            for s, sym in enumerate(symbol):
                if virtual:
                # special conditions
                    if sym == 'penalty':
                        self.layout['_PENALTY'] = message[s].to(self.engine.context)
                        message[s] = '_PENALTY'
                    elif sym == 'is_train':
                        self.layout['_IS_TRAIN'] = message[s]
                    continue
                elif sym == 'is_train':
                    continue
                args += (self.layout[component.message[s]],)
            if virtual:
                self._parameters[node_name] = component.component.parameters()
                self._states[node_name] = component.component.state_dict()
                return node_name
            if node_name in self.ID:  # Reuse or Redefine an existent node
                assert len(message) == 1  # the only way to reuse is invoking DUPLICATE with single input
                hull = self._getHull(message[0])
                self.blueprint._drawNode(message[0], node_name, hull)
                return node_name
            if assemblage is None:
                self.layout[node_name] = component.component(*args)
                self.ID.add(node_name)
                if symbol[0] == 'penalty':
                    self.blueprint._drawNode(node_name, node_name, visible=False)
            else:
                if symbol[0] == 'penalty':
                    self.layout[node_name] = component.component(*args)
                    self.ID.add(node_name)
                    self.blueprint._drawNode(node_name, node_name, visible=False)
                else: # message includes input at least
                    args = (self.layout[assemblage],) + args[1:]
                    self.layout[node_name] = component.component(*args)
                    self.ID.add(node_name)
                    # draw layout sheet
                    hull = self._getHull(assemblage)
                    self.blueprint._drawNode(assemblage, node_name, hull)
            for msg in message:
                # draw layout sheet
                if msg[0]!='_' and symbol[0]!='penalty':
                    hull = self._getHull(msg)
                    self.blueprint._drawNode(msg, node_name, hull)
            return node_name

    def _finalize(self, first_call):
        if first_call:
            for k in self.terminator.keys():
                self.layout[k] = None
        else:
            for k in self.terminator.keys():
                self.layout[k] = self.terminator[k].component(media=(self._parameters, self.layout['_PENALTY']))

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
            self.comp += self.module[-1][0]._build(self._ImpSym.tensors_in)
            assemblage = self._assemble(comp, sub_scope=sub_scope, virtual=True)
        return assemblage

    def fillUp(self, name, shape, dtype):
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