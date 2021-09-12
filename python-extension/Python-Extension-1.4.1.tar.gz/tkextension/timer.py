# -*- coding:utf-8  -*-

import sys
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    raise SystemExit('This module needs Python 3.4 or more later')

from tkinter import *
from tkinter.messagebox import *
import tkextension.tix as tix
import time

class Timer(tix.Layout):
    def __init__(self, window, mode='timer', arg=0):
        self.end = False
        self.tk = window
        self.mode = mode
        if mode == 'timer':
            self.window = Label(window, text=0)
        elif mode == 'down count':
            self.time = arg
            self.window = Label(window, text=self.time)
        elif mode == 'alarm clock':
            self.time = arg
        else:
            raise AttributeError(''' 'Time' object has no attribute '%s' ''' % mode)
    def timer(per1second):
        psecond = per1second % 100
        # Per 1 S
        second = per1second // 100
        while second >= 60:
            second -= 60
        # S
        minute = per1second // 100 // 60
        while minute >= 60:
            minute -= 60
        # Min
        hour = per1second // 100 // 60 // 60
        while hour >= 24:
            hour -= 24
        # H
        day = per1second // 100 // 60 // 60 // 24
        # D
        return '%s : %s : %s : %s : %s' % (day, hour, minute, second, psecond)
    def mainloop(self):
        if self.mode == 'timer':
            per1second = 0
            while self.end != True:
                self.window.config(text=Timer.timer(per1second))
                self.tk.update()
                time.sleep(0.01)
                per1second += 1
        elif self.mode == 'down count':
            while self.time > 0:
                self.window.config(text=Timer.timer(self.time))
                self.tk.update()
                time.sleep(0.01)
                self.time -= 1
        elif self.mode == 'alarm clock':
            while self.time > 0:
                self.tk.update()
                time.sleep(0.01)
                self.time -= 1
    def stop(self):
        self.end == True
