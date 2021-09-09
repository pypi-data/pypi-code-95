#! /usr/bin/python3

from tkinter.constants import W
from commind.core.node import Node
import tkinter
from commind.core.engine import Engine


class App(tkinter.Frame):
    def __init__(self,master):
        super().__init__(master)
        self.config(width=1024,height=768)
        self.pack()

        self.canvas = tkinter.Canvas(self)
        self.canvas.config(width=1024,height=768,bg='white')
        self.canvas.grid(row=0)

        self.entrythingy = tkinter.Entry(self)
        self.entrythingy.config(width=80)
        self.entrythingy.grid(row=1)

        self.contents = tkinter.StringVar()
        self.contents.set('input command here')

        self.entrythingy['textvariable'] = self.contents
        self.entrythingy.bind('<Key>',self.char)

        self.entrythingy.bind_all('<Control-;>',self.set_focus)
        self.engine = Engine(self.canvas)
        self.engine.refresh()

    def char(self,event):
        if event.char == '\r':
            self.engine.exec(self.contents.get())
            self.contents.set('')
        _text = self.contents.get()
        _text = _text.lstrip()
        self.contents.set(_text)
        self.engine.refresh()
    
    def set_focus(self,event):
        self.contents.set('')
        self.entrythingy.focus()

def run():
    mainwindow = tkinter.Tk()
    mainwindow.title('PyComMind v0.0.0')
    App(mainwindow).mainloop()