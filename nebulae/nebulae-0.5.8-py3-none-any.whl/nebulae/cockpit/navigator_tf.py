#!/usr/bin/env python
'''
navigator_tf
Created by Seria at 04/02/2019 4:48 PM
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
import time
from glob import glob
from collections import defaultdict
import os
from ..toolkit import parseConfig, recordConfig
from .navigator import Stage





class NavigatorTF(object):
    roman_numeral = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    def __init__(self, dashboard, time_machine, fuel_depot, spacedock):
        self.db = dashboard
        self.tm = time_machine
        self.fd = fuel_depot
        self.sd = spacedock
        if spacedock is None:
            self.flag_empty = True
        else:
            self.flag_empty = False
        self.propellants = defaultdict(list)
        self.epoch = 0
        self.mile = 0
        self.mpe = 0
        self.stage = 'UNKNOWN'
        # start a session
        self.sess = tf.Session(config=self.sd.engine.config_proto)
        self.sess.run(tf.global_variables_initializer())
        miles = []
        scopes = []
        for sc in spacedock._spacecraft:
            craft = getattr(spacedock, sc)
            miles.append(craft.holder['_MEDIA'])
            scopes.append(craft.scope)
        self.feed(Stage.START, time_machine._setParams, external=False,
                            sess=self.sess, mile=sum(miles), scope='-'.join(scopes))

    def feed(self, stage, propellant, position=None, external=True, **kwargs):
        if external:
            kwargs['nvg'] = self
        if isinstance(position, int):
            quantity = len(self.propellants[stage])
            if position < quantity:
                self.propellants[stage][position] = (propellant, kwargs)
            else:
                for p in range(quantity, position):
                    self.propellants[stage].append((None, 'False'))
        self.propellants[stage].append((propellant, kwargs))

    def _airDrop(self, stage, n, **kwargs):
        # kwargs.update(self.propellants[stage][n][2])
        self.propellants[stage][n] = self.propellants[stage][n][0:2] + (kwargs,)

    def _triggerStage(self, curr_stage):
        self.stage = curr_stage
        for ppl, kwargs in self.propellants[curr_stage]:
            ppl(**kwargs)

    def cruise(self, craft, back=None, forth=None, **entrance):
        '''
        craft: spacecraft
        back: loss name
        forth: optimizer name
        entrance: input (formated as keyword arguments)
        '''
        ent = {}
        for k in entrance.keys():
            ent[craft.holder[k]] = entrance[k]

        if forth is None:
            entrance[forth] = None
        # tensors with initial letter being '_' in names should be systematic
        ext = {k: craft.holder[k] for k in craft.holder.keys() if k not in entrance.keys() and k[0]!='_'}
        ret = self.sess.run(list(ext.values()), ent)

        for i, key in enumerate(ext.keys()):
            craft[key] = ret[i]

    def execute(self):
        root_stage = self.stage
        for stg in Stage.groups[root_stage]:
            self._triggerStage(stg)
        self.stage = root_stage

    def _scribe(self):
        if self.flag_empty:
            bp_cfg = {}
        else:
            bp_cfg = {}
            for sc in self.sd._spacecraft:
                bp_cfg[sc] = getattr(self.sd, sc).blueprint.param
        config = {'NG': self.sd.engine.param, 'TM': self.tm.param,
                  'FD': {}, 'SD': {}, 'DB': self.db.param, 'BP': bp_cfg}
        ft = self.fd.tanks
        for k in ft.keys():
            config['FD'][k] = ft[k].param

        temp_configs = glob(os.path.join(os.getcwd(), 'nebulae_temp_config*.json'))
        # if there are more or less than one optimizer in a SC, error would be reported
        for cfg in temp_configs:
            hyper_param = parseConfig(cfg)
            idx = len(os.path.basename(cfg)) - 24
            config['SD'][self.sd._spacecraft[idx]] = hyper_param
            os.remove(cfg)
        if not os.path.exists(self.tm.param['save_path']):
            os.mkdir(self.tm.param['save_path'])
        recordConfig(os.path.join(self.tm.param['save_path'], 'config.json'), config)

    def log(self, gauge=True, tachograph=True, blueprint=True, setting=True):
        self.feed(Stage.END, self.db._log, external=False, gauge=gauge, tachograph=tachograph)

        if blueprint:
            for sc in self.sd._spacecraft:
                self.feed(Stage.START, getattr(self.sd, sc).blueprint.log, external=False,
                          log_dir=self.db.param['log_path'], graph_name=sc)
        if setting:
            self.feed(Stage.START, self._scribe, external=False)

    def launch(self):
        try:
            print('+' + 35 * '-' + '+')
            print('| The Spacecraft is being launched. |')
            print('+' + 35 * '-' + '+')
            self._triggerStage(Stage.START)
            self._triggerStage(Stage.RUN)
            self._triggerStage(Stage.END)
            print('+' + 44 * '-' + '+')
            print('| The Spacecraft has arrived at destination. |')
            print('+' + 44 * '-' + '+')

        except BaseException as e:
            if Stage.BREAK_DOWN in self.propellants:
                self._triggerStage(Stage.BREAK_DOWN)
            else:
                raise e