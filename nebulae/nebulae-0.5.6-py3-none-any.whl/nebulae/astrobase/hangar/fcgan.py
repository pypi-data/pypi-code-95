#!/usr/bin/env python
'''
garage
Created by Seria at 03/01/2019 8:32 PM
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
from .. import dock



class Generator(dock.Craft):
    def __init__(self, in_shape, latent_dim, scope='GEN'):
        super(Generator, self).__init__(scope)
        H, W, C = in_shape
        assert H%4==0 and W%4==0
        self.H = H
        self.W = W
        self.C = C

        self.lrelu = dock.LRelu()

        self.fc_1 = dock.Dense(latent_dim, 128 * (H // 4) * (W // 4))
        self.bn_1 = dock.BN(128, dim=2)
        pad = dock.autoPad((H // 2, W // 2), (3, 3), stride=2)
        self.conv_1 = dock.TransConv(128, 128, (H // 2, W // 2), kernel=(3, 3), stride=2, padding=pad)
        self.bn_2 = dock.BN(128, dim=2, mmnt=0.2)
        pad = dock.autoPad((H, W), (3, 3), stride=2)
        self.conv_2 = dock.TransConv(128, 64, (H, W), kernel=(3, 3), stride=2, padding=pad)
        self.bn_3 = dock.BN(64, dim=2, mmnt=0.2)
        pad = dock.autoPad((H, W), (3, 3))
        self.conv_3 = dock.Conv(64, C, (3, 3), padding=pad)

        self.tanh = dock.Tanh()
        self.reshape = dock.Reshape()

    def run(self, z):
        self['latent_code'] = z
        z = self.fc_1(self['latent_code'])
        z = self.reshape(z, (-1, 128, self.H//4, self.W//4))

        z = self.bn_1(z)
        z = self.conv_1(z)

        z = self.bn_2(z)
        z = self.lrelu(z)
        z = self.conv_2(z)

        z = self.bn_3(z)
        z = self.lrelu(z)
        z = self.conv_3(z)

        self['fake'] = self.tanh(z)

        return self['fake']


class Discriminator(dock.Craft):
    def __init__(self, in_shape, scope='DSC'):
        super(Discriminator, self).__init__(scope)
        H, W, C = in_shape
        self.H = H
        self.W = W
        self.C = C

        self.lrelu = dock.LRelu()
        self.flat = dock.Reshape()
        pad = dock.autoPad((H, W), (3, 3), stride=2)
        self.conv_1 = dock.Conv(C, 16, (3, 3), stride=2, padding=pad)
        pad = dock.autoPad((ceil(H/2), ceil(W/2)), (3, 3), stride=2)
        self.conv_2 = dock.Conv(16, 32, (3, 3), stride=2, padding=pad)
        self.bn_2 = dock.BN(32, dim=2, mmnt=0.2)
        pad = dock.autoPad((ceil(H/4), ceil(W/4)), (3, 3), stride=2)
        self.conv_3 = dock.Conv(32, 64, (3, 3), stride=2, padding=pad)
        self.bn_3 = dock.BN(64, dim=2, mmnt=0.2)
        pad = dock.autoPad((ceil(H/8), ceil(W/8)), (3, 3), stride=2)
        self.conv_4 = dock.Conv(64, 128, (3, 3), stride=2, padding=pad)
        self.bn_4 = dock.BN(128, dim=2, mmnt=0.2)
        self.cls = dock.Dense(ceil(H/16) * ceil(W/16) * 128, 1)

    def run(self, x):
        bs = x.shape[0]
        self['input'] = x
        x = self.conv_1(x)
        x = self.lrelu(x)

        x = self.conv_2(x)
        x = self.lrelu(x)
        x = self.bn_2(x)

        x = self.conv_3(x)
        x = self.lrelu(x)
        x = self.bn_3(x)

        x = self.conv_4(x)
        x = self.lrelu(x)
        x = self.bn_4(x)

        x = self.flat(x, (bs, -1))
        self['out'] = self.cls(x)

        return self['out']



class FCGAN(dock.Craft):
    def __init__(self, in_shape, latent_dim=128, scope='FCGAN'):
        super(FCGAN, self).__init__(scope)
        self.G = Generator(in_shape, latent_dim)
        self.D = Discriminator(in_shape)

    def run(self):
        pass