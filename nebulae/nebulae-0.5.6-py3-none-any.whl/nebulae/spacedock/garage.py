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
from .spacecraft import SpaceCraft
from .component import Component
from os.path import basename

class Garage(object):
    def __init__(self, channel_major=True, time_major=False):
        self.channel_major = channel_major
        self.time_major = time_major
        self.VGG_16 = self.vgg_16
        self.RESNET_V2_50 = self.resnet_v2_50
        self.RESNET_V2_101 = self.resnet_v2_101
        self.RESNET_V2_152 = self.resnet_v2_152
        self.SE_RESNET_V2_50 = self.se_resnet_v2_50
        self.SE_RESNET_V2_101 = self.se_resnet_v2_101
        self.SE_RESNET_V2_152 = self.se_resnet_v2_152

    def _residual(self, inputs, shallow, deep, stride, name):
        COMP = Component(self.channel_major, self.time_major)
        input, is_train = inputs
        res_block = (COMP.CONV(name=name + '_conv_pre', input=input, kernel=[1, 1],
                              stride=[stride, stride], out_chs=shallow)
                    >> COMP.BATCH_NORM(name=name + '_bn_mid', is_train=is_train)
                    >> COMP.RELU(name=name + '_relu_mid')
                    >> COMP.CONV(name=name + '_conv_mid', kernel=[3, 3], out_chs=shallow)
                    >> COMP.BATCH_NORM(name=name + '_bn_post', is_train=is_train)
                    >> COMP.RELU(name=name + '_relu_post')
                    >> COMP.CONV(name=name + '_conv_post', kernel=[1, 1], out_chs=deep))
        return res_block

    def _bottleNeckRes(self, sc, inputs, shallow, deep, scope, name, down_sample=False, pre_activate=True):
        COMP = Component(self.channel_major, self.time_major)
        input, is_train = inputs
        if pre_activate:
            input = sc.assemble(COMP.BATCH_NORM(name=name + '_bn_pre',
                                                  input=input, is_train=is_train)
                                  >> COMP.RELU(name=name + '_relu_pre'), sub_scope=scope)
        if down_sample:
            stride = 2
            idt_path = (COMP.CONV(name=name+'_conv_idt', input=input,
                                  kernel=[1, 1], stride=[2, 2], out_chs=deep))
        else:
            stride = 1
            if pre_activate:
                idt_path = (COMP.DUPLICATE(name=basename(input), input=input))
            else:
                idt_path = (COMP.CONV(name=name + '_conv_idt', input=input, kernel=[1, 1], out_chs=deep))

        res_path = self._residual((input, is_train), shallow, deep, stride, name)
        return sc.assemble(idt_path + res_path, sub_scope=scope)

    def _bottleNeckSE(self, sc, inputs, shallow, deep, scope, name, down_sample=False, pre_activate=True):
        COMP = Component(self.channel_major, self.time_major)
        input, is_train = inputs
        if pre_activate:
            input = sc.assemble(COMP.BATCH_NORM(name=name + '_bn_pre',
                                                input=input, is_train=is_train)
                                >> COMP.RELU(name=name + '_relu_pre'), sub_scope=scope)
        if down_sample:
            stride = 2
            idt_path = (COMP.CONV(name=name + '_conv_idt', input=input,
                                  kernel=[1, 1], stride=[2, 2], out_chs=deep))
        else:
            stride = 1
            if pre_activate:
                idt_path = (COMP.DUPLICATE(name=basename(input), input=input))
            else:
                idt_path = (COMP.CONV(name=name + '_conv_idt', input=input, kernel=[1, 1], out_chs=deep))

        res_path = sc.assemble(self._residual((input, is_train),
                                               shallow, deep, stride, name), sub_scope=scope)
        se_path = (COMP.DUPLICATE(name=basename(res_path), input=res_path)
                   * self._squeezeExicitation(res_path, shallow//4, deep, name))

        return sc.assemble(idt_path + se_path, sub_scope=scope)

    def _squeezeExicitation(self, input, shallow, deep, name):
        COMP = Component(self.channel_major, self.time_major)
        se_block = (COMP.AVG_POOL(name=name+'_se_avg_pool', input=input, keep_size=False, if_global=True)
                    >> COMP.CONV(name=name+'_se_down', kernel=[1,1], out_chs=shallow)
                    >> COMP.RELU(name=name+'_se_relu')
                    >> COMP.CONV(name=name+'_se_up', kernel=[1,1], out_chs=deep)
                    >> COMP.SIGMOID(name=name+'_se_sigm'))
        return se_block

    def vgg_16(self, sc, inputs, p_drop=0.5, scope='VGG_16'):
        COMP = Component(self.channel_major, self.time_major)
        COMP.addComp('conv_3x3', COMP.CONV(name='conv_3x3', kernel=[3, 3]))
        conv1 = (COMP.CONV_3X3(name='conv1_1', input=inputs, out_chs=64)
                 >> COMP.RELU(name='relu1_1')
                 >> COMP.CONV_3X3(name='conv1_2', out_chs=64)
                 >> COMP.RELU(name='relu1_2')
                 >> COMP.MAX_POOL(name='max_pool1'))
        conv2 = ((COMP.CONV_3X3(name='conv2', out_chs=128)
                 >> COMP.RELU(name='relu2')) ** 2
                 >> COMP.MAX_POOL(name='max_pool2'))
        conv3 = ((COMP.CONV_3X3(name='conv3', out_chs=256)
                 >> COMP.RELU(name='relu3')) ** 3
                 >> COMP.MAX_POOL(name='max_pool3'))
        conv4 = ((COMP.CONV_3X3(name='conv4', out_chs=512)
                 >> COMP.RELU(name='relu4')) ** 3
                 >> COMP.MAX_POOL(name='max_pool4'))
        conv5 = ((COMP.CONV_3X3(name='conv5', out_chs=512)
                     >> COMP.RELU(name='relu5')) ** 3
                 >> COMP.MAX_POOL(name='max_pool5'))
        gconv6 = (COMP.CONV(name='gconv6', kernel=[7, 7], out_chs=4096, keep_size=False)
                 >> COMP.DROPOUT(name='dropout6', p_drop=p_drop))
        gconv7 = (COMP.CONV(name='gconv7', kernel=[1, 1], out_chs=4096)
                 >> COMP.DROPOUT(name='dropout7', p_drop=p_drop))
        net = sc.assemble(conv1 >> conv2 >> conv3 >> conv4 >> conv5 >> gconv6 >> gconv7, sub_scope=scope)
        return net

    def resnet_v2_50(self, sc, input, is_train, scope='Res_50'):
        return self._resnet_v2(sc, input, is_train, scope, [3, 4, 6, 3])

    def resnet_v2_101(self, sc, input, is_train, scope='Res_101'):
        return self._resnet_v2(sc, input, is_train, scope, [3, 4, 23, 3])

    def resnet_v2_152(self, sc, input, is_train, scope='Res_152'):
        return self._resnet_v2(sc, input, is_train, scope, [3, 8, 36, 3])

    def _resnet_v2(self, sc, input, is_train, scope, blocks):
        COMP = Component(self.channel_major, self.time_major)
        net = sc.assemble(COMP.CONV(name='conv0', input=input,
                                    kernel=[7, 7], stride=[2, 2], out_chs=64)
                 >> COMP.MAX_POOL(name='max_pool0', kernel=[3, 3]), sub_scope=scope)
        # building block 1
        net = self._bottleNeckRes(sc, [net, is_train], 64, 256, scope, pre_activate=False, name='block1_0')
        for l in range(1, blocks[0]):
            net = self._bottleNeckRes(sc, [net, is_train], 64, 256, scope, name='block1_'+str(l))
        # building block 2
        net = self._bottleNeckRes(sc, [net, is_train], 128, 512, scope, down_sample=True, name='block2_0')
        for l in range(1, blocks[1]):
            net = self._bottleNeckRes(sc, [net, is_train], 128, 512, scope, name='block2_'+str(l))
        # building block 3
        net = self._bottleNeckRes(sc, [net, is_train], 256, 1024, scope, down_sample=True, name='block3_0')
        for l in range(1, blocks[2]):
            net = self._bottleNeckRes(sc, [net, is_train], 256, 1024, scope, name='block3_' + str(l))
        # building block 4
        net = self._bottleNeckRes(sc, [net, is_train], 512, 2048, scope, down_sample=True, name='block4_0')
        for l in range(1, blocks[3]):
            net = self._bottleNeckRes(sc, [net, is_train], 512, 2048, scope, name='block4_' + str(l))
        return sc.assemble(COMP.AVG_POOL(name='avg_pool', input=net,
                                         kernel=[7, 7], keep_size=False, if_global=True), sub_scope=scope)

    def se_resnet_v2_50(self, sc, input, is_train, scope='SE_Res_50'):
        return self._se_resnet_v2(sc, input, is_train, scope, [3, 4, 6, 3])

    def se_resnet_v2_101(self, sc, input, is_train, scope='SE_Res_101'):
        return self._se_resnet_v2(sc, input, is_train, scope, [3, 4, 23, 3])

    def se_resnet_v2_152(self, sc, input, is_train, scope='SE_Res_152'):
        return self._se_resnet_v2(sc, input, is_train, scope, [3, 8, 36, 3])

    def _se_resnet_v2(self, sc, input, is_train, scope, blocks):
        COMP = Component(self.channel_major, self.time_major)
        net = sc.assemble(COMP.CONV(name='conv0', input=input,
                                    kernel=[7, 7], stride=[2, 2], out_chs=64)
                 >> COMP.MAX_POOL(name='max_pool0', kernel=[3, 3]), sub_scope=scope)
        # building block 1
        net = self._bottleNeckSE(sc, [net, is_train], 64, 256, scope, pre_activate=False, name='block1_0')
        for l in range(1, blocks[0]):
            net = self._bottleNeckSE(sc, [net, is_train], 64, 256, scope, name='block1_'+str(l))
        # building block 2
        net = self._bottleNeckSE(sc, [net, is_train], 128, 512, scope, down_sample=True, name='block2_0')
        for l in range(1, blocks[1]):
            net = self._bottleNeckSE(sc, [net, is_train], 128, 512, scope, name='block2_'+str(l))
        # building block 3
        net = self._bottleNeckSE(sc, [net, is_train], 256, 1024, scope, down_sample=True, name='block3_0')
        for l in range(1, blocks[2]):
            net = self._bottleNeckSE(sc, [net, is_train], 256, 1024, scope, name='block3_' + str(l))
        # building block 4
        net = self._bottleNeckSE(sc, [net, is_train], 512, 2048, scope, down_sample=True, name='block4_0')
        for l in range(1, blocks[3]):
            net = self._bottleNeckSE(sc, [net, is_train], 512, 2048, scope, name='block4_' + str(l))
        return sc.assemble(COMP.AVG_POOL(name='avg_pool', input=net,
                                         kernel=[7, 7], keep_size=False, if_global=True), sub_scope=scope)