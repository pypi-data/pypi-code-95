#!/usr/bin/env python
'''
component
Created by Seria at 25/11/2018 2:58 PM
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
import mxnet as mx
from copy import deepcopy
from functools import partial
from ..law import Law

class Pod:
    def __init__(self, comp, symbol, name, msg=[], info=None):
        self.component = comp
        self.symbol = symbol
        self.message = msg
        self.name = name
        self.info = info

    def __rshift__(self, other):
        return Pod([self, other], '>', 'CASCADE', info={'type': 'OPERAND'})

    def __add__(self, other):
        return Pod([self, other], '+', 'ADD', info={'type': 'OPERAND'})

    def __sub__(self, other):
        return Pod([self, other], '-', 'SUB', info={'type': 'OPERAND'})

    def __mul__(self, other):
        return Pod([self, other], '*', 'MUL', info={'type': 'OPERAND'})

    def __matmul__(self, other):
        return Pod([self, other], '@', 'MATMUL', info={'type': 'OPERAND'})

    def __and__(self, other):
        return Pod([self, other], '&', 'CONCAT', info={'type': 'OPERAND'})

    def __pow__(self, power, modulo=None):
        assert isinstance(power, int)
        pod = deepcopy(self)
        pod._appendSerialNo('0')
        for p in range(1, power):
            pod_temp = deepcopy(self)
            pod_temp._appendSerialNo(str(p))
            pod = pod >> pod_temp
        return pod

    def _appendSerialNo(self, serial_no):
        if isinstance(self.component, list):
            self.component[0]._appendSerialNo(serial_no)
            self.component[1]._appendSerialNo(serial_no)
        else:
            self.name += '_' + serial_no

    def _build(self, base):
        if isinstance(self.component, list):
            comp_child = []
            comp_child += self.component[0]._build(base)
            comp_child += self.component[1]._build(base)
            return comp_child
        else:
            _base = {}
            for key in base.keys():
                if key in self.symbol:
                    if key == 'input':
                        _base[key] = base[self.info['full_name']]
                    else:
                        _base[key] = base[key]
            self.component = partial(self.component, **_base)
            self.component = self.component()
            return [self.component]

    def _isOptz(self):
        # 1:  this is an optimizer
        # 0:  this pod has a component followed by an optimizer
        # -1: this pod is a normal component
        if isinstance(self.component, list):
            if self.component[1].symbol[-1] == 'media':
                return 0
            else:
                return -1
        else:
            if self.symbol[-1]=='media':
                return 1
            else:
                return -1



def Component(channel_major=True, time_major=False):
    core = Law.CORE.upper()
    if core == 'TENSORFLOW':
        from .component_tf import ComponentTF
        return ComponentTF(channel_major, time_major)
    elif core == 'MXNET':
        from .component_mx import ComponentMX
        return ComponentMX(channel_major, time_major)
    elif core == 'PYTORCH':
        from .component_pt import ComponentPT
        return ComponentPT(channel_major, time_major)
    else:
        raise ValueError('NEBULAE ERROR ⨷ %s is an unsupported core.' % core)