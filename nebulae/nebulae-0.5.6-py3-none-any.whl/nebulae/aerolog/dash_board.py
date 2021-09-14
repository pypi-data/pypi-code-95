#!/usr/bin/env python
'''
dash_board
Created by Seria at 29/12/2018 3:29 PM
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
import matplotlib.pyplot as plt
import scipy.misc as misc
import numpy as np
import os.path as path
import time

class DashBoard(object):
    palette = ['#F08080', '#00BFFF', '#FFFF00', '#2E8B57', '#6A5ACD', '#FFD700', '#808080']
    linestyle = ['-', '--', '-.', ':']
    def __init__(self, config=None, log_path='./aerolog', window=1, format=None):
        '''
        :param config:
        :param window: the window length of moving average
        :param format: a list of which the element is format and mode, e.g. ['3f', 'raw']
        '''
        if config is None:
            self.param = {'log_path': log_path, 'window': window, 'format': format}
        else:
            config['window'] = config.get('window', window)
            self.param = config
        self.max_epoch = 0
        self.win_mile = {}
        self.gauge_mile = {}
        self.gauge_epoch = {}
        self.trail_mile = {}
        self.trail_epoch = {}

    def _getOridinal(self, number):
        remainder = number % 10
        if remainder == 1:
            ordinal = 'st'
        elif remainder == 2:
            ordinal = 'nd'
        elif remainder == 3:
            ordinal = 'rd'
        else:
            ordinal = 'th'
        return ordinal

    def _formatAsStr(self, stage, abbr, value, global_mile=-1):
        format, mode = self.param['format'][abbr]
        format = '%-' + format
        if mode == 'raw':
            return (' %%s ➠ \033[1;36m%s\033[0m |' % format) % (abbr, value)
        elif mode == 'percent':
            return (' %%s ➠ \033[1;36m%s%%%%\033[0m |' % format) % (abbr, value*100)
        elif mode == 'image':
            if global_mile >= 0:
                misc.imsave(path.join(self.param['log_path'], '%s/%s_%d.jpg'%(stage, abbr, global_mile)))
            return ''
        else:
            raise KeyError('%s is an illegal format option.' % mode)

    def _gauge(self, items, mile, epoch, mpe, duration, interval):
        epoch += 1
        string_mile = ''
        stage = 'UNKNOWN'
        flag_display = False
        flag_epoch_end = False
        if mile % interval == 0:
            flag_display = True
        if (mile+1) % mpe == 0:
            flag_epoch_end = True
            if epoch > self.max_epoch:
                self.max_epoch = epoch
            string_epoch = ''
            cnt = 0
        if mile == 0:
            self.time = time.time()
        for name, value in items:
            # read gauge every mile
            global_mile = ((epoch-1)*mpe+mile)
            if flag_display:
                stage, abbr = name.split(':')
                string_mile += self._formatAsStr(stage, abbr, value, global_mile)
            if name not in self.win_mile.keys():
                self.win_mile[name] = np.zeros((self.param['window'],))
                self.gauge_mile[name] = []
                self.gauge_epoch[name] = [0]
                self.trail_mile[name] = []
                self.trail_epoch[name] = []
            self.win_mile[name][global_mile % self.param['window']] = value
            self.gauge_epoch[name][-1] += value
            if global_mile < self.param['window']:
                gauge = np.array(self.win_mile[name][:global_mile+1]).mean()
            else:
                gauge = np.array(self.win_mile[name]).mean()
            self.gauge_mile[name].append(gauge)
            self.trail_mile[name].append(global_mile)
            if flag_epoch_end:
                # read gauge every epoch
                stage, abbr = name.split(':')
                self.gauge_epoch[name][-1] /= mpe
                self.trail_epoch[name].append(epoch)
                indicator = self._formatAsStr(stage, abbr, self.gauge_epoch[name][-1])
                string_epoch += indicator
                if indicator != '':
                    cnt += 1
                self.gauge_epoch[name].append(0)
        if flag_display:
            ordinal = self._getOridinal(epoch)
            progress = int(mile / mpe * 10 + 0.4)
            yellow_bar = progress * ' '
            space_bar = (10 - progress) * ' '
            print('| %d%s Epoch ✇ %d Miles ⊰⟦\033[43m%s\033[0m%s⟧⊱︎ ⧲ %.3fs/mile | %s |%s     '
                  % (epoch, ordinal, mile, yellow_bar, space_bar, duration, stage, string_mile), end='\r')
        if flag_epoch_end:
            ordinal = self._getOridinal(epoch)
            mileage = str(epoch * mpe)
            display = '| %d%s Epoch ✇ %s Miles ︎⧲ %.2fs/epoch | %s |%s' \
                      % (epoch, ordinal, mileage, time.time() - self.time, stage, string_epoch)
            print('+' + (len(display) - 3 - cnt * 11) * '-' + '+' + 30 * ' ')
            print(display)
            print('+' + (len(display) - 3 - cnt * 11) * '-' + '+' + 30 * ' ')
            self.time = time.time()

    def _gaugeEpoch(self, names, epoch, mpe, duration, interval):
        epoch += 1
        if epoch > self.max_epoch:
            self.max_epoch = epoch
        string = ''
        stage = 'UNKNOWN'
        cnt = 0
        flag_display = False
        if epoch % interval == 0:
            flag_display = True
        for name in names:
            stage, abbr = name.split(':')
            self.gauge_epoch[name][-1] /= mpe
            self.trail_epoch[name].append(epoch)
            if flag_display:
                indicator = self._formatAsStr(stage, abbr, self.gauge_epoch[name][-1])
                string += indicator
                if indicator != '':
                    cnt += 1
            self.gauge_epoch[name].append(0)
        if flag_display:
            ordinal = self._getOridinal(epoch)
            mileage = str(epoch*mpe)
            display = '| %d%s Epoch ✇ %s Miles ︎⧲ %.2fs/epoch | %s |%s' \
                      % (epoch, ordinal, mileage, duration, stage, string)
            print('+' + (len(display) - 3 - cnt * 11) * '-' + '+' + 30 * ' ')
            print(display)
            print('+' + (len(display) - 3 - cnt * 11) * '-' + '+' + 30 * ' ')

    def log(self):
        boards = {}
        # clustering
        for k in self.param['format'].keys():
            boards[k] = []
        for k in self.gauge_mile.keys():
            boards[k.split(':')[-1]].append(k)
        # plot
        for k in boards.keys():
            for i, b in enumerate(boards[k]):
                plt.plot(self.trail_mile[b], self.gauge_mile[b], c=self.palette[i%7], label=b)
                plt.legend()
                plt.grid(True)
                plt.savefig(path.join(self.param['log_path'], '%s%d_%.3g_mile_%d.jpg'
                                      % (k, i, self.gauge_mile[b][-1], self.trail_mile[b][-1])))
                plt.close()

            for i, b in enumerate(boards[k]):
                plt.plot(self.trail_epoch[b], self.gauge_epoch[b][:-1], marker='o',
                         c=self.palette[i%7], linestyle=self.linestyle[i%4], label=b)
            if self.max_epoch > 0:
                plt.legend()
                plt.grid(True)
                plt.savefig(path.join(self.param['log_path'], '%s_epoch_%d.jpg' % (k, self.max_epoch)))
                plt.close()