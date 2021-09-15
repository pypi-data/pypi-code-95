import tkinter as tk
from .style import Style
from .styles import DEFAULT

class Tk(tk.Tk):
    def __init__(self, *args, style=Style(), **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.set_style(DEFAULT)

    def set_style(self, style: Style):
        style.apply(self)
