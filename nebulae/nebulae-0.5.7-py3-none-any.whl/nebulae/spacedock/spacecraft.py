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

def SpaceCraft(engine, blueprint, scope=''):
    core = Law.CORE.upper()
    if core == 'TENSORFLOW':
        from .spacecraft_tf import SpaceCraftTF
        return SpaceCraftTF(engine, blueprint, scope)
    elif core == 'MXNET':
        from .spacecraft_mx import SpaceCraftMX
        return SpaceCraftMX(engine, blueprint, scope)
    elif core == 'PYTORCH':
        from .spacecraft_pt import SpaceCraftPT
        return SpaceCraftPT(engine, blueprint, scope)
    else:
        raise ValueError('NEBULAE ERROR ⨷ %s is an unsupported core.' %core)