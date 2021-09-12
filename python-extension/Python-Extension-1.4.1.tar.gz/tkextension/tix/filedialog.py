# -*- coding:utf-8  -*-

from tkinter import *
import tkextension.tix as tix
import platform as p
import os

class FileTree(tix.Layout):
    def __init__(self, tkinter_attribute, filetypes=[('All Files', '')], path=None, width=200, height=200):
        self.filetypes = filetypes
        self.location = ''
        if p.system() == 'Windows':
            self.done = ['C:\\']
        elif p.system() == 'Darwin':
            self.done = ['/Users']
        elif p.system() == 'Linux':
            self.done = ['/home']
        self.redo = []
        # Value
        self.tk = tkinter_attribute
        self.frame = Frame(self.tk, width=width, height=height)
        # Tkinter
        self.tree = Listbox(self.frame)
        self.tree.place(relx=0.5, rely=0.5, relwidth=0.96, relheight=0.8, anchor='center')
        self.entry = Entry(self.frame)
        self.entry.place(relx=0.5, rely=0.05, relwidth=0.96, relheight=0.1, anchor='center')
        self.undo_btn = Button(self.frame, text='Undo', command=self.undo)
        self.undo_btn.place(relx=0.15, rely=0.95, relwidth=0.3, relheight=0.1, anchor='center')
        # Window
        if p.system() == 'Windows':
            if path == None:
                self.location = 'C:\\'
            else:
                self.location = path
            self.entry.insert('end', self.location)
            self.items = os.listdir(self.location)
        elif p.system() == 'Darwin':
            if path == None:
                self.location = '/Users'
            else:
                self.location = path
            self.entry.insert('end', self.location)
            self.items = os.listdir(self.location)
        elif p.system() == 'Linux':
            if path == None:
                self.location = '/home'
            else:
                self.location = path
            self.entry.insert('end', self.location)
            self.items = os.listdir(self.location)
        else:
            raise SystemExit('System \'%s\' is not supported' % p.system())
        # Items
        self.entry.bind('<Any-KeyRelease>', self.relist)
        self.tree.bind('<Double-Button-1>', self.into)
        # Bind
        self.done.append(self.entry.get())
        # Value
        self.update()
    def relist(self, event=None, mode='entry'):
        if mode == 'entry':
            self.location = self.entry.get()
        try:
            self.items = os.listdir(self.location)
            if mode == 'into':
                self.entry.delete(0, 'end')
                self.entry.insert('end', self.location)
        except OSError:
            self.entry.delete(0, 'end')
            self.entry.insert('end', self.location)
        self.done.append(self.location)
        self.update()
    def into(self, event=None):
        try:
            os.listdir(self.location)
            if p.system() == 'Windows':
                self.location = self.location + '\\' + self.tree.get('active')
            elif p.system() == 'Darwin':
                self.location = self.location + '/' + self.tree.get('active')
        except OSError:
            pass
        self.relist(mode='into')
    def update(self):
        types = []
        for x in self.filetypes:
            if type(x) == type(()):
                for y in x:
                    types.append(y)
            else:
                types.append(x)
        self.tree.delete(0, 'end')
        for x in self.items:
            for y in x[::-1]:
                if y == '.':
                    index = x[::-1].find(y)
                    index = len(x) - 1 - index
                    string = x[index:]
                    if string in types:
                        self.tree.insert('end', x)
                    break
            else:
                self.tree.insert('end', x)
    def undo(self):
        print(self.done)
        self.redo.append(self.location)
        self.entry.delete(0, 'end')
        self.entry.insert('end', self.done[-2])
        self.location = self.entry.get()
        del self.done[-2]
        self.relist(mode='undo')
    def get(self):
        self.location = self.entry.get()
        try:
            data = os.listdir(self.location)
        except OSError:
            data = self.location
        return data
