# -*- coding:utf-8  -*-

import sys
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    raise SystemExit('This module needs Python 3.4 or more later')

from tkinter import *
from tkinter.colorchooser import *
from tkextension import *
import tkextension.tix as tix

class BlackBoard(tix.Layout):
    def __init__(self, tkinter_attribute, width=400, height=200, bg='#ffffff'):
        self.color = 'black'
        self.width = 1
        self.x = width // 2
        self.y = height // 2
        self.on_slide = ['off']
        # Value
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk)
        self.canvas = Canvas(self.frame, width=width, height=height, bg=bg)
        self.canvas.pack()
        lb = LabelFrame(self.frame, text='Tools')
        lb.pack()
        self.colorchoose_btn = Button(lb, text='A', command=self.colorchoose)
        self.colorchoose_btn.grid(column=0, row=0)
        self.width_btn = Button(lb, text='Width ( W )', command=self.widthset)
        self.width_btn.grid(column=0, row=1)
        self.motion_on_btn = Button(lb, text='Turn on slide painting ( O )', command=self.onslide, state='normal')
        self.motion_on_btn.grid(column=1, row=0)
        self.motion_off_btn = Button(lb, text='Turn off slide painting ( F )', command=self.offslide, state='disabled')
        self.motion_off_btn.grid(column=1, row=1)
        self.clean_btn = Button(lb, text='Clear', command=(lambda x = 'all' : self.canvas.delete(x)))
        self.clean_btn.grid(column=0, row=2, columnspan=2)
        # Window
        self.canvas.bind_all('<Key-A>', self.colorchoose)
        self.canvas.bind_all('<Key-W>', self.widthset)
        self.canvas.bind_all('<Key-O>', self.onslide)
        self.canvas.bind_all('<Key-F>', self.offslide)
        self.canvas.bind_all('<Key-C>', (lambda x = 'all' : self.canvas.delete(x)))
        self.canvas.bind('<Button-1>', self.linex)
        self.canvas.bind('<ButtonRelease-2>', self.liney)
        self.canvas.bind('<ButtonRelease-1>', self.draw)
        self.canvas.bind('<Motion>', self.mdraw)
        # Bind
    def draw(self, event):
        x1, y1 = (event.x - self.width), (event.y - self.width)
        x2, y2 = (event.x + self.width), (event.y + self.width)
        self.canvas.create_oval(x1, y1, x2, y2, fill=self.color)
    def mdraw(self, event):
        if self.on_slide[-1] == 'on':
            x1, y1 = (event.x - self.width), (event.y - self.width)
            x2, y2 = (event.x + self.width), (event.y + self.width)
            self.canvas.create_oval(x1, y1, x2, y2, fill=self.color)
    def linex(self, event):
        self.x = event.x
        self.y = event.y
    def liney(self, event):
        self.canvas.create_line(self.x, self.y, event.x, event.y, fill=self.color)
    def onslide(self, event=None):
        self.on_slide.append('on')
        self.motion_on_btn.config(state='disabled')
        self.motion_off_btn.config(state='normal')
    def offslide(self, event=None):
        self.on_slide.append('off')
        self.motion_on_btn.config(state='normal')
        self.motion_off_btn.config(state='disabled')
    def colorchoose(self, event=None):
        self.color = askcolor()
        self.color = self.color[1]
        self.colorchoose_btn.config(text='A', fg=self.color)
    def widthset(self, event=None):
        self.width = int(askanswer('', 'Width'))
