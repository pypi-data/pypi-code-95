#!/usr/bin/env python
'''
navigator
Created by Seria at 23/12/2018 11:21 AM
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
from ..law import Law

class Stage(object):
    START = 'START'
    RUN = 'RUN'
    END = 'END'
    BREAK_DOWN = 'BREAK_DOWN'
    stages = [START, RUN, END, BREAK_DOWN]
    groups = {START:[], RUN:[], END:[], BREAK_DOWN:[]}
    @classmethod
    def register(cls, group, stage):
        for s,stg in enumerate(stage):
            stg = stg.upper()
            stage[s] = stg
            if stg in cls.stages:
                raise Exception('NEBULAE ERROR ⨷ %s is an existing component in warehouse.' % stage)
            else:
                exec('Stage.%s = "%s"' % (stg, stg))
                cls.stages.append(stg)

        group = group.upper()
        if group not in cls.groups.keys():
            raise KeyError('NEBULAE ERROR ⨷ there is no group named %s.' % group)
        else:
            cls.groups[group].extend(stage)
        # initialize an empty group
        for stg in stage:
            cls.groups[stg] = []



def Navigator(dashboard, time_machine, fuel_depot, spacecraft=None):
    core = Law.CORE.upper()
    if core == 'TENSORFLOW':
        from .navigator_tf import NavigatorTF
        return NavigatorTF(dashboard, time_machine, fuel_depot, spacecraft)
    elif core == 'MXNET':
        from .navigator_mx import NavigatorMX
        return NavigatorMX(dashboard, time_machine, fuel_depot, spacecraft)
    elif core == 'PYTORCH':
        from .navigator_pt import NavigatorPT
        return NavigatorPT(dashboard, time_machine, fuel_depot, spacecraft)
    else:
        raise ValueError('NEBULAE ERROR ⨷ %s is an unsupported core.' % core)