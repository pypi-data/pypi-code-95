# -*- coding=utf-8 -*-

import sys
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    raise SystemExit('This module needs Python 3.4 or more later')

from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
import pickle
import time

class Pack():
    def pack(self, **options):
        return self.frame.pack(**options)
    def pack_forget(self):
        return self.frame.pack_forget()
    def pack_info(self):
        return self.frame.pack_info(self)

class Grid():
    def grid(self, **options):
        return self.frame.grid(**options)
    def grid_forget(self):
        return self.frame.grid_forget()
    def grid_info(self):
        return self.frame.pack_info(self)
    def grid_bbox(self, column=None, row=None, col2=None, row2=None):
        return self.frame.grid_bbox(column, row, col2, row2)
    def grid_columnconfigure(self, index, **options):
        return self.frame.grid_columnconfigure(index, **options)
    def grid_rowconfigure(self, index, **options):
        return self.frame.grid_rowconfigure(index, **options)
    def grid_location(self, x, y):
        return self.frame.grid_location(x, y)
    def grid_remove(self):
        return self.frame.grid_remove()
    def grid_size(self):
        return self.frame.grid_size()

class Place():
    def place(self, **options):
        return self.frame.place(**options)
    def place_forget(self):
        return self.frame.forget()
    def place_info(self):
        return self.frame.pack_info(self)

class Layout(Pack, Grid, Place):
    def forget(self):
        return self.frame.forget()

class AskValue(Layout):
    def __init__(self, tkinter_attribute, msg='', args=(0, 100), get=False):
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk)
        # Tkinter
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.label.pack()
        if type(args[0]) == type(0):
            self.sb = Scale(self.frame, from_=args[0], to=args[1], orient='horizontal')
        elif type(args[0]) == type('0'):
            self.sb = Spinbox(self.frame, values=args, wrap=True)
        else:
            raise TypeError('%s\'s items must be int or string')
        self.sb.pack()
        if get == True:
            Button(self.frame, text='OK', command=self.get).pack()
        # Window
    def config(self, msg=''):
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.label.pack()
        else:
            self.label.forget()
    def get(self):
        return self.sb.get()

class AskItem(Layout):
    def __init__(self, tkinter_attribute, msg='', items=['a', 'b', 'c'], number=1, normal=0, get=False):
        self.items = items
        self.number = number
        self.normal = normal
        # Value
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk)
        # Tkinter
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.label.place(relx=0.5, rely=0.05, relwidth=1, relheight=0.1, anchor='center')
        self.lb = Listbox(self.frame)
        self.lb.pack()
        self.lb.selection_set(normal)
        if get == True:
            Button(self.frame, text='OK', command=self.get).pack()
        # Window
        for x in range(0, len(items)):
            self.lb.insert('end', items[x])
        # Load
    def config(self, msg=''):
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.label.pack()
        else:
            self.label.forget()
    def get(self):
        finish = False
        get = []
        for x in range(0, len(self.items)):
            if self.lb.selection_includes(x) == 1:
                get.append(x)
        # Get
        if len(get) == self.number:
            finish = True
        else:
            get.append(self.normal)
        return get

class AskAnswer(Layout):
    def __init__(self, tkinter_attribute, msg='', get=False):
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk)
        # Tkinter
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.label.pack()
        self.entry = Entry(self.frame, width=30)
        self.entry.pack()
        if get == True:
            Button(self.frame, text='Finish', command=self.get).pack()
        # Window
    def config(self, msg=''):
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.label.pack()
        else:
            self.label.forget()
    def get(self):
        return self.entry.get()

class ControlBoard(Layout):
    def __init__(self, tkinter_attribute, msg='', item=[('scale', '', 1, 100), ('listbox', '', [1, 2, 3])], get=False):
        self.item = item
        # Value
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk)
        # Tkinter
        self.text = Text(self.frame)
        self.text.pack()
        # Text
        if msg != '':
            text.insert('end', msg)
            text.insert('end', '\n')
        # Label
        self.window = []
        self.window_list = []
        for x in item:
            if x[0] == 'scale':
                self.window.append(Scale(self.frame, from_=x[2], to=x[3], orient='horizontal'))
                self.window_list.append('scale')
            elif x[0] == 'listbox':
                self.window.append(Listbox(self.frame))
                self.window_list.append('listbox')
                for y in x[2]:
                    self.window[-1].insert('end', y)
        for x in range(0, len(item)):
            self.text.insert('end', item[x][1])
            self.text.insert('end', '\n')
            self.text.window_create('end', window=self.window[x])
            self.text.insert('end', '\n')
        # Scale & Listbox
        if get == True:
            button = Button(self.frame, text='Finish', command=self.get)
            self.text.window_create('end', window=button)
        # Button
        self.text.config(state='disabled')
        # Window
    def get(self):
        result = []
        for x in (0, len(self.window) - 1):
            if self.window_list[x] == 'scale':
                result.append(self.window[x].get())
            elif self.window_list[x] == 'listbox':
                for y in range(0, len(self.item[x][2])):
                    if self.window[x].selection_includes(y) == 1:
                        result.append(self.item[x][2][y])
                        break
                if len(result) < x + 1:
                    result.append(self.item[x][2][0])
            else:
                raise SystemExit
        return result

class SingleChoice(Layout):
    def __init__(self, tkinter_attribute, msg='', args=('a', 'b', 'c'), get=False):
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk)
        # Tkinter
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.label.pack()
        window = []
        self.v = StringVar()
        for x in args:
            window.append(Radiobutton(self.frame, text=x, variable=self.v, value=x))
        for x in window:
            x.pack()
        if get == True:
            Button(self.frame, text='Finish', command=self.get).pack()
        # Window
    def config(self, msg=''):
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.label.pack()
        else:
            self.label.forget()
    def get(self):
        return self.v.get()

class SingleChoices(Layout):
    def __init__(self, tkinter_attribute, msg='', args=(('a', 'b', 'c'), ('e', 'f', 'g')), get=False):
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk)
        # Tkinter
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.label.pack()
        # Label
        self.value_list = []
        lf_list = []
        times = 0
        for x in args:
            self.value_list.append(StringVar())
            # Value
            lf_list.append(LabelFrame(self.frame, text=str(times + 1)))
            lf_list[-1].pack()
            # LabelFrame
            for y in x:
                Radiobutton(lf_list[times], text=y, variable=self.value_list[times], value=y).pack(side='left')
            # Tkinter
            times += 1
        # Checkbutton
        if get == True:
            Button(tk, text='Finish', command=self.get).pack()
        # Button
        # Window
    def config(self, msg=''):
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.label.pack()
        else:
            self.label.forget()
    def get(self):
        get = []
        for x in self.value_list:
            get.append(x.get())
        return get

class AnswerSheet(Layout):
    def __init__(self, tkinter_attribute, msg='', args=[('a', 'b', 'c')], answer=['a'], points=[1], get=False):
        self.answer = answer
        self.points = points
        # Value
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk)
        # Tkinter
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.label.pack()
        # Label
        self.value_list = []
        lf_list = []
        times = 0
        for x in args:
            self.value_list.append(StringVar())
            # Value
            lf_list.append(LabelFrame(self.frame, text=str(times + 1)))
            lf_list[-1].pack()
            # LabelFrame
            for y in x:
                Radiobutton(lf_list[times], text=y, variable=self.value_list[times], value=y).pack(side='left')
            # Tkinter
            times += 1
        # Checkbutton
        if get == True:
            Button(self.frame, text='Finish', command=self.get).pack()
        # Button
        # Window
    def config(self, msg=''):
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.label.pack()
        else:
            self.label.forget()
    def get(self):
        get = []
        for x in self.value_list:
            get.append(x.get())
        # Get
        point = 0
        for x in range(0, len(get)):
            if get[x] == self.answer[x]:
                point += self.points[x]
        return [get, point]
