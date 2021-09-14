#!/usr/bin/env python
'''
time_machine_tf
Created by Seria at 04/02/2019 4:35 PM
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
from mxnet.gluon import nn, SymbolBlock, HybridBlock
import os
from glob import glob


class Dock():
    def __init__(self, sd):
        self.scope = sd._spacecraft
        self.ctx = sd.engine.device
        self._craft = {}
        for sc in sd._spacecraft:
            craft = getattr(sd, sc)
            self._craft[sc] = craft


class TimeMachineMX(object):
    def __init__(self, param):
        '''
        Time Machine saves current states or restores saved states
        '''
        self.param = param

    def _setParams(self, spacedock):
        self.counter = 0
        self.sd = Dock(spacedock)

    def backTo(self, ckpt_scope=None, frozen=False, ins=None, outs=None):
        if ckpt_scope is not None:
            print('NEBULAE WARNING ⧆ ckpt_scope does not work in mxnet core.')
        if self.param['ckpt_path'] is None:
            raise Exception('NEBULAE ERROR ⨷ anchor location is not provided.')
        else:
            for sc in self.sd.scope:
                architecture = glob(os.path.join(self.param['ckpt_path'],'%s*.params'%sc))
                max_saved = -1
                for arch in architecture:
                    saved_no = int(arch.split('.')[0].split('-')[-1])
                    if saved_no > max_saved:
                        moment = arch
                        max_saved = saved_no

                if frozen:
                    self.sd._craft[sc].load_parameters(moment, self.sd.ctx)
                else:
                    missing = True
                    extra = True
                    self.sd._craft[sc].load_parameters(moment, self.sd.ctx, allow_missing=missing, ignore_extra=extra)
            print('+' + ((10 + len(self.param['ckpt_path'])) * '-') + '+')
            print('| Back to \033[1;34m%s\033[0m |' % self.param['ckpt_path'])
            print('+' + ((10 + len(self.param['ckpt_path'])) * '-') + '+')

    def dropAnchor(self, save_scope=None, frozen=False, anchor=None):
        if save_scope is not None:
            print('NEBULAE WARNING ⧆ save_scope does not work in mxnet core.')
        if self.param['save_path'] is None:
            raise Exception('NEBULAE ERROR ⨷ there is nowhere to drop anchor.')
        else:
            for sc in self.sd.scope:
                if frozen:
                    self.sd._craft[sc].export(os.path.join(self.param['save_path'], sc), epoch=self.counter)
                save_ckpt = os.path.join(self.param['save_path'], '%s-%d.params'%(sc, self.counter))
                self.sd._craft[sc].save_parameters(save_ckpt)
            self.counter += 1
            print('| Anchor is dropped at \033[1;34m%s\033[0m |' % self.param['save_path'])