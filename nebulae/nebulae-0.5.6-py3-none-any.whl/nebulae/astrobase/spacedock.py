# !/usr/bin/env python
'''
space_craft
Created by Seria at 23/11/2018 10:31 AM
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
from glob import glob
import os


class SpaceDock(object):
    def __init__(self, engine):
        object.__setattr__(self, 'core', Law.CORE.upper())
        object.__setattr__(self, 'engine', engine)
        object.__setattr__(self, '_spacecraft', [])
        # clear cache
        temp_configs = glob(os.path.join(os.getcwd(), 'nebulae_temp_config*.json'))
        for cfg in temp_configs:
            os.remove(cfg)

    def __setattr__(self, scope, blueprint):
        if hasattr(self, scope):
            raise ValueError('NEBULAE ERROR ⨷ a spacecraft named %s has already been there.'%scope)
        if self.core == 'TENSORFLOW':
            from .spacedock_tf import SpaceCraftTF
            sc = SpaceCraftTF(self.engine.device, blueprint, scope, self.__getattribute__)
            object.__setattr__(self, scope, sc)
        elif self.core == 'MXNET':
            from .spacedock_mx import SpaceCraftMX
            sc = SpaceCraftMX(self.engine.device, blueprint, scope, self.__getattribute__)
            object.__setattr__(self, scope, sc)
        elif self.core == 'PYTORCH':
            from .spacedock_pt import SpaceCraftPT
            sc = SpaceCraftPT(self.engine.device, blueprint, scope, self.__getattribute__)
            object.__setattr__(self, scope, sc)
        else:
            raise ValueError('NEBULAE ERROR ⨷ %s is an unsupported core.' %self.core)
        self._spacecraft.append(scope)

# def SpaceCraft(engine, blueprint, scope):
#     core = Law.CORE.upper()
#     if core == 'TENSORFLOW':
#         from .spacedock_tf import SpaceCraftTF
#         return SpaceCraftTF(engine.device, blueprint, scope)
#     elif core == 'MXNET':
#         from .spacedock_mx import SpaceCraftMX
#         return SpaceCraftMX(engine.device, blueprint, scope)
#     elif core == 'PYTORCH':
#         from .spacedock_pt import SpaceCraftPT
#         return SpaceCraftPT(engine.device, blueprint, scope)
#     else:
#         raise ValueError('NEBULAE ERROR ⨷ %s is an unsupported core.' %core)