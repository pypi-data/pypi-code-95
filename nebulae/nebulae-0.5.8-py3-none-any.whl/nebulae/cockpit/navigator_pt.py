#!/usr/bin/env python
'''
navigator_pt
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
import torch
import torch.nn as nn
import numpy as np
import time
from glob import glob
from collections import defaultdict
import os
from ..toolkit import parseConfig, recordConfig
from .navigator import Stage



class NavigatorPT(object):
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
        self.feed(Stage.START, time_machine._setParams, external=False, spacedock=spacedock)
        for sc in spacedock._spacecraft:
            craft = getattr(spacedock, sc)
            self.feed(Stage.START, craft._finalize, external=False, first_call=True) # finalize the architecture
            self.feed(Stage.RUN, craft._finalize, external=False, first_call=False)

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
        ent = []
        inp = []
        for k in entrance.keys():
            if isinstance(entrance[k], np.ndarray) and k in craft.in_node:
                ent.append(torch.from_numpy(entrance[k].astype(craft._launcher[k][1])).to(craft.device))
                inp.append(k)
            elif isinstance(entrance[k], torch.Tensor) and k in craft.in_node:
                ent.append(entrance[k].to(craft.device))
                inp.append(k)
        craft.in_node = inp

        ext = ()
        if back is not None:
            ext = ext + (back,)

        if forth is None:
            craft.out_node = ext
            craft.eval()
            with torch.no_grad():
                ret = craft(*tuple(ent))
        else:
            ext = ext + (forth,)
            craft.out_node = ext
            craft.train()
            ret = craft(*tuple(ent))
            ret[forth].optimizer.zero_grad()
            ret[back].backward()
            ret[forth].optimizer.step()
            ret[forth].step()

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
                getattr(self.sd, sc).blueprint._await = True
                getattr(self.sd, sc).blueprint._path = os.path.join(self.db.param['log_path'], sc)
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