import tkinter as tk

class OverlayWindow(tk.Toplevel):
    def __init__(self, *args, bg='white', **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.overrideredirect(True)
        self.bind('<Configure>', self.__set_transparency_color)
        self.state('zoomed')
        self.configure(background=bg)
        self.lift()
        self.wm_attributes("-topmost", True)

    def __set_transparency_color(self, event):
        self.wm_attributes("-transparentcolor", self['background'])
