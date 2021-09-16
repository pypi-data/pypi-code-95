#!/usr/bin/env python
'''
engine_mx
Created by Seria at 12/02/2019 3:45 PM
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
from ..toolkit.utility import getAvailabelGPU

class EngineMX(object):
    '''
    Param:
    device: 'gpu' or 'cpu'
    available_gpus
    gpu_mem_fraction
    if_conserve
    least_mem
    '''
    def __init__(self, param):
        self.param = param
        # look for available gpu devices
        if self.param['device'].lower() == 'gpu':
            if self.param['if_conserve']:
                from os import environ
                environ['MXNET_GPU_MEM_POOL'] = str(int(100 * self.param['gpu_mem_fraction']))
            if len(self.param['available_gpus']) == 0:
                gpus = getAvailabelGPU(self.param['ngpus'], self.param['least_mem'])
            else:
                gpus = self.param['available_gpus']
            if len(gpus) < self.param['ngpus']:
                raise Exception('NEBULAE ERROR ⨷ no enough available gpu.')
            elif self.param['ngpus'] == 1:
                self.device = mx.gpu(gpus[0])
            else:
                self.device = [mx.gpu(idx) for idx in gpus]
            # convert gpu list to string
            gpustr = ''
            for g in gpus:
                gpustr += str(g) + ','
            gpus = gpustr[:-1]
            print('+' + ((24 + len(gpus)) * '-') + '+')
            print('| Reside in Device: \033[1;36mGPU-%s\033[0m |' % gpus)
            print('+' + ((24 + len(gpus)) * '-') + '+')
        elif self.param['device'].lower() == 'cpu':
            self.device = mx.cpu()
            print('+' + (23 * '-') + '+')
            print('| Reside in Device: \033[1;36mCPU\033[0m |')
            print('+' + (23 * '-') + '+')
        else:
            raise KeyError('NEBULAE ERROR ⨷ given device should be either cpu or gpu.')