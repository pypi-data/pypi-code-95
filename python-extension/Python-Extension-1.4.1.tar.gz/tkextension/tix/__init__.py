# -*- coding:utf-8  -*-

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
    def __init__(self, tkinter_attribute, msg='', args=(0, 100)):
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
    def __init__(self, tkinter_attribute, msg='', items=['a', 'b', 'c'], number=1, normal=0, width=35, height=15):
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
        if width != None and height != None:
            self.lb = Listbox(self.frame, width=width, height=height)
        elif width != None:
            self.lb = Listbox(self.frame, width=width)
        elif height != None:
            self.lb = Listbox(self.frame, height=height)
        else:
            self.lb = Listbox(self.frame)
        self.lb.pack()
        self.lb.selection_set(normal)
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
    def __init__(self, tkinter_attribute, msg='', width=30, validate=None, validatecommand=None, invalidcommand=None):
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk)
        # Tkinter
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.label.pack()
        if validate != None:
            self.entry = Entry(self.frame, width=width)
        else:
            if invalidcommand == None:
                self.entry = Entry(self.frame, width=width, validate=validate, validatecommand=validatecommand)
            else:
                self.entry = Entry(self.frame, width=width, validate=validate, validatecommand=validatecommand, invalidcommand=invalidcommand)
        self.entry.pack()
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
    def __init__(self, tkinter_attribute, msg='', msg_variable=None, item=[('scale', '', 1, 100), ('listbox', '', [1, 2, 3]), ('radiobutton', '', '1', 'IntVar()', 1)], width=35, height=15):
        self.item = item
        # Value
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk)
        # Tkinter
        self.text = Text(self.frame, width=width, height=height)
        self.text.pack()
        # Text
        if msg != '' or msg_variable != None:
            if msg_variable != None:
                self.label = Label(self.frame, variable=msg_variable)
            else:
                self.label = Label(self.frame, text=msg)
            self.text.window_create('end', window=self.label)
            self.text.insert('end', '\n')
        # Label
        self.window = []
        self.window_list = []
        self.value_list = []
        for x in item:
            if x[0] == 'scale':
                self.window.append(Scale(self.frame, from_=x[2], to=x[3], orient='horizontal'))
                self.window_list.append('scale')
            elif x[0] == 'listbox':
                self.window.append(Listbox(self.frame))
                self.window_list.append('listbox')
                for y in x[2]:
                    self.window[-1].insert('end', y)
            elif x[0] == 'radiobutton':
                self.value_list.append(x[3])
                self.window.append(Radiobutton(self.frame, text=x[2], variable=x[3], value=x[4]))
                self.window_list.append('radiobutton')
        for x in range(0, len(item)):
            if item[x][1] != '':
                self.text.insert('end', item[x][1])
            self.text.window_create('end', window=self.window[x])
            self.text.insert('end', '\n')
        # Scale & Listbox
        self.text.config(state='disabled')
        # Window
    def config(self, msg=''):
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.text.window_create('1.0', window=self.label)
            self.text.insert('1.1', '\n')
        else:
            self.label.forget()
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
            elif self.window_list[x] == 'radiobutton':
                result.append(self.item[x][3].get())
            else:
                raise SystemExit
        return result

class SingleChoices(Layout):
    def __init__(self, tkinter_attribute, msg='', msg_variable=None, args=(('a', 'b', 'c'), ('e', 'f', 'g')), width=35, height=15):
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk)
        # Tkinter
        self.text = Text(self.frame, width=width, height=height)
        self.text.pack()
        # Text
        if msg != '' or msg_variable != None:
            if msg_variable != None:
                self.label = Label(self.frame, variable=msg_variable)
            else:
                self.label = Label(self.frame, text=msg)
            self.text.window_create('end', window=self.label)
            self.text.insert('end', '\n')
        # Label
        self.value_list = []
        lf_list = []
        times = 0
        for x in args:
            if type(x[0]) == type(1):
                self.value_list.append(IntVar())
            else:
                self.value_list.append(StringVar())
            # Value
            lf_list.append(LabelFrame(self.frame, text=str(times + 1)))
            self.text.window_create('end', window=lf_list[-1])
            self.text.insert('end', '\n')
            # LabelFrame
            for y in x:
                Radiobutton(lf_list[times], text=y, variable=self.value_list[times], value=y).pack(side='left')
            # Tkinter
            times += 1
        # Checkbutton
        self.text.config(state='disabled')
        # Window
    def config(self, msg=''):
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.text.window_create('1.0', window=self.label)
            self.text.insert('1.1', '\n')
        else:
            self.label.forget()
    def get(self):
        get = []
        for x in self.value_list:
            get.append(x.get())
        return get

class AnswerSheet(Layout):
    def __init__(self, tkinter_attribute, msg='', msg_variable=None, args=[('a', 'b', 'c')], answer=['a'], points=[1], width=35, height=15):
        self.answer = answer
        self.points = points
        # Value
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk)
        # Tkinter
        self.text = Text(self.frame, width=width, height=height)
        self.text.pack()
        # Text
        if msg != '' or msg_variable != None:
            if msg_variable != None:
                self.label = Label(self.frame, variable=msg_variable)
            else:
                self.label = Label(self.frame, text=msg)
            self.text.window_create('end', window=self.label)
            self.text.insert('end', '\n')
        # Label
        self.value_list = []
        lf_list = []
        times = 0
        for x in args:
            if type(x[0]) == type(1):
                self.value_list.append(IntVar())
            else:
                self.value_list.append(StringVar())
            # Value
            lf_list.append(LabelFrame(self.frame, text=str(times + 1)))
            self.text.window_create('end', window=lf_list[-1])
            self.text.insert('end', '\n')
            # LabelFrame
            for y in x:
                Radiobutton(lf_list[times], text=y, variable=self.value_list[times], value=y).pack(side='left')
            # Tkinter
            times += 1
        # Checkbutton
        self.text.config(state='disabled')
        # Window
    def config(self, msg=''):
        if msg != '':
            self.label = Label(self.frame, text=msg)
            self.text.window_create('1.0', window=self.label)
            self.text.insert('1.1', '\n')
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
