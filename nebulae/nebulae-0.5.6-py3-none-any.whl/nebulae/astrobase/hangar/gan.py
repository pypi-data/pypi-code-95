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
from .. import dock



class MLPG(dock.Craft):
    def __init__(self, in_shape, latent_dim, scope='MLPG'):
        super(MLPG, self).__init__(scope)
        H, W, C = in_shape
        self.H = H
        self.W = W
        self.C = C

        self.lrelu = dock.LRelu()
        self.fc_1 = dock.Dense(latent_dim, latent_dim)
        self.fc_2 = dock.Dense(latent_dim, latent_dim * 2)
        self.bn_2 = dock.BN(latent_dim * 2, dim=1, mmnt=0.2)
        self.fc_3 = dock.Dense(latent_dim * 2, latent_dim * 4)
        self.bn_3 = dock.BN(latent_dim * 4, dim=1, mmnt=0.2)
        self.fc_4 = dock.Dense(latent_dim * 4, latent_dim * 8)
        self.bn_4 = dock.BN(latent_dim * 8, dim=1, mmnt=0.2)

        self.fc_pixel = dock.Dense(latent_dim * 8, H * W * C)
        self.tanh = dock.Tanh()
        self.rect = dock.Reshape()

    def run(self, z):
        self['latent_code'] = z
        z = self.fc_1(self['latent_code'])
        z = self.lrelu(z)

        z = self.fc_2(z)
        z = self.bn_2(z)
        z = self.lrelu(z)

        z = self.fc_3(z)
        z = self.bn_3(z)
        z = self.lrelu(z)

        z = self.fc_4(z)
        z = self.bn_4(z)
        z = self.lrelu(z)

        z = self.fc_pixel(z)
        z = self.tanh(z)
        self['fake'] = self.rect(z, (-1, self.C, self.H, self.W))

        return self['fake']


class MLPD(dock.Craft):
    def __init__(self, in_shape, latent_dim, scope='MLPD'):
        super(MLPD, self).__init__(scope)
        H, W, C = in_shape
        self.H = H
        self.W = W
        self.C = C

        self.lrelu = dock.LRelu()
        self.flat = dock.Reshape()
        self.fc_1 = dock.Dense(H * W * C, latent_dim * 2)
        self.fc_2 = dock.Dense(latent_dim * 2, latent_dim)
        self.cls = dock.Dense(latent_dim, 1)

    def run(self, x):
        self['input'] = x
        x = self.flat(self['input'], (-1, self.C * self.H * self.W))
        x = self.fc_1(x)
        x = self.lrelu(x)
        x = self.fc_2(x)
        x = self.lrelu(x)

        self['out'] = self.cls(x)

        return self['out']



class GAN(dock.Craft):
    def __init__(self, in_shape, latent_dim=128, scope='GAN'):
        super(GAN, self).__init__(scope)
        self.G = MLPG(in_shape, latent_dim)
        self.D = MLPD(in_shape, latent_dim)

    def run(self):
        pass