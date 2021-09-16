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
import os
import torch
from ..toolkit.utility import getAvailabelGPU

class EnginePT(object):
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
            # convert gpu list to string
            gpustr = ''
            for g in gpus:
                gpustr += str(g) + ','
            gpus = gpustr[:-1]
            # set environment variable
            os.environ['CUDA_VISIBLE_DEVICES'] = gpus
            self.device = [torch.device('cuda:%d'%i) for i in range(self.param['ngpus'])]
            print('+' + ((24 + len(gpus)) * '-') + '+')
            print('| Reside in Device: \033[1;36mGPU-%s\033[0m |' % gpus)
            print('+' + ((24 + len(gpus)) * '-') + '+')
        elif self.param['device'].lower() == 'cpu':
            self.device = ['cpu']
            print('+' + (23 * '-') + '+')
            print('| Reside in Device: \033[1;36mCPU\033[0m |')
            print('+' + (23 * '-') + '+')
        else:
            raise KeyError('NEBULAE ERROR ⨷ given device should be either cpu or gpu.')

    def coat(self, datum):
        if datum.shape==(): # scalar
            return torch.tensor(datum)
        if self.param['device'] == 'gpu':
            return torch.from_numpy(datum).cuda()
        elif self.param['device'] == 'cpu':
            return torch.from_numpy(datum).cpu()
        else:
            raise KeyError('NEBULAE ERROR ⨷ given device should be either cpu or gpu.')

    def shell(self, datum):
        if datum.size == 1:
            return datum.detach().cpu().numpy()[0]
        else:
            return datum.detach().cpu().numpy()