#!/usr/bin/env python
'''
Created by Seria at 02/11/2018 3:38 PM
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

from math import ceil
import matplotlib.pyplot as plt
import os

from .fuel_tank import FuelTank

class FuelDepot(object):
    def __init__(self):
        self.tanks = {} # contains all fuel tanks
        self.fetcher = {} # contains batch fetcher of all tanks
        self.modifiable_keys = ['name', 'batch_size', 'if_shuffle', 'height', 'width', 'channel', 'resol_ratio',
                                'complete_last_batch', 'spatial_aug', 'p_sa', 'temporal_aug', 'p_ta']

    def load(self, config=None, name=None, batch_size=None, if_shuffle=True,
                 data_path=None, data_key=None, is_encoded=True, height=0, width=0,
                channel=3, frame=0, rescale=True, resol_ratio=1, complete_last_batch=True,
                 spatial_aug='', p_sa=(), theta_sa=(),
                 temporal_aug='', p_ta=(), theta_ta=()):
        if config is None:
            config = {}
            config['name'] = name
            config['batch_size'] = batch_size
            config['data_path'] = data_path
            config['data_key'] = data_key
            config['is_encoded'] = is_encoded
            config['if_shuffle'] = if_shuffle
            config['height'] = height
            config['width'] = width
            config['channel'] = channel
            config['rescale'] = rescale
            config['resol_ratio'] = resol_ratio
            config['complete_last_batch'] = complete_last_batch
            config['frame'] = frame
            config['spatial_aug'] = spatial_aug
            config['p_sa'] = p_sa
            config['theta_sa'] = theta_sa
            config['temporal_aug'] = temporal_aug
            config['p_ta'] = p_ta
            config['theta_ta'] = theta_ta
        else:
            config['if_shuffle'] = config.get('if_shuffle', if_shuffle)
            config['is_encoded'] = config.get('is_encoded', is_encoded)
            config['height'] = config.get('height', height)
            config['width'] = config.get('width', width)
            config['channel'] = config.get('channel', channel)
            config['rescale'] = config.get('rescale', rescale)
            config['resol_ratio'] = config.get('resol_ratio', resol_ratio)
            config['complete_last_batch'] = config.get('complete_last_batch', complete_last_batch)
            config['frame'] = config.get('frame', frame)
            config['spatial_aug'] = config.get('spatial_aug', spatial_aug)
            config['p_sa'] = config.get('p_sa', p_sa)
            config['theta_sa'] = config.get('theta_sa', theta_sa)
            config['temporal_aug'] = config.get('temporal_aug', temporal_aug)
            config['p_ta'] = config.get('p_ta', p_ta)
            config['theta_ta'] = config.get('theta_ta', theta_ta)
        if config['name'] in self.tanks:
            raise Exception('%s is already mounted.' % name)
        if not os.path.exists(config['data_path']):
            raise ValueError('There is no such file or directory named %s.' % config['data_path'])
        self.tanks[config['name']] = FuelTank(config)
        self.fetcher[config['name']] = self.tanks[config['name']]._fetchBatches()

    def unload(self, tank=''):
        name_err = Exception('NEBULAE ERROR ⨷ %s is not an mounted fuel tank.' % tank)
        if tank != '' and (tank not in self.tanks.keys()):
            raise name_err
        elif tank == '':
            for t in list(self.tanks.keys()):
                self.fetcher.pop(t)
                self.tanks.pop(t)
        else:
            self.fetcher.pop(tank)
            self.tanks.pop(tank)

    def next(self, name, visible=False):
        batch = self.fetcher[name].__next__()
        if visible:
            param = self.tanks[name].param
            if param['rescale']:
                plt.imshow((batch[param['data_key']][0]+1)/2)
            else:
                plt.imshow(batch[param['data_key']][0])
            plt.show()
        return batch

    @property
    def epoch(self):
        epochs = {}
        for t in self.tanks.keys():
            epochs[t] = abs(self.tanks[t].epoch)+1
        return epochs

    @property
    def MPE(self):
        MPEs = {}
        for t in self.tanks.keys():
            MPEs[t] = ceil(self.tanks[t].nsample/self.tanks[t].param['batch_size'])
        return MPEs

    @property
    def volume(self):
        volumes = {}
        for t in self.tanks.keys():
            volumes[t] = self.tanks[t].nsample
        return volumes

    def modify(self, tank='', config=None, **kwargs):
        flag_rename = False
        if config:
            kwargs = config
        for key in kwargs:
            if key not in self.modifiable_keys:
                raise KeyError('NEBULAE ERROR ⨷ %s is not a modifiable parameter or has not been defined.'%key)
            elif key == 'name':
                flag_rename = True
                assert tank!='', 'NEBULAE ERROR ⨷ rename all tanks to same one is illegal.'
                self.tanks[tank].param[key] = kwargs[key]
            else:
                if tank == '':
                    for t in self.tanks.values():
                        t.param[key] = kwargs[key]
                else:
                    self.tanks[tank].param[key] = kwargs[key]
        if flag_rename:
            self.tanks[kwargs['name']] = self.tanks[tank]
            self.tanks.pop(tank)
            self.fetcher[kwargs['name']] = self.fetcher[tank]
            self.fetcher.pop(tank)