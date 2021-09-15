import tkinter as tk
from .color import Color
from .mixins import Reactive

class TabbedFrame(tk.Frame):
    def __init__(self, *args, tabs=tuple(), allow_tab_creation=False, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.fg_color = Color.from_hex(self.option_get('foreground','Foreground'))
        self.bg_color = Color.from_hex(self.option_get('background','Background'))

        self._topbar = tk.Frame(self)
        self._topbar.pack(side=tk.TOP, fill=tk.X, anchor=tk.N)
        
        self._tabs = {}
        for tabname in tabs:
            self.create_tab(tabname)

        if allow_tab_creation:
            self._newtab_frame = tk.Frame(self._topbar)
            self._newtab_button = Reactive(tk.Button(self._newtab_frame, anchor=tk.CENTER, text='+', command=self._on_newtab_button))
            self._newtab_underline = tk.Frame(self._newtab_frame, height=1, background = self.option_get('foreground','Foreground'))
            self._newtab_button.pack(side=tk.TOP)
            self._newtab_underline.pack(side=tk.BOTTOM, fill=tk.X)
            self._newtab_frame.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_button(self, tabname):
        for name, (frame, spacer, button) in self._tabs.items():
            if name != tabname:
                frame.pack_forget()
                spacer.config(background=self.fg_color.as_hex(), height=1)
                button.config(foreground=self.fg_color.as_hex())
            else:
                frame.pack(fill=tk.BOTH, expand=True)
                spacer.config(background=self.fg_color.lighter().as_hex(), height=2)
                button.config(foreground=self.fg_color.lighter().as_hex())

    def _on_newtab_button(self):
        def entry_callback(e: tk.Event):
            name = self._newtab_input.get()
            if len(name.replace(' ','')) == 0: return
            if name in self._tabs.keys(): return
            self._newtab_input.delete(0, tk.END)
            self.create_tab(name)
            self._newtab_input.pack_forget()
            self._newtab_button.pack(side=tk.TOP)

        self._newtab_button.pack_forget()
        self._newtab_input = tk.Entry(self._newtab_frame)
        self._newtab_input.insert(0, 'new tab')
        self._newtab_input.select_range(0, tk.END)
        self._newtab_input.bind('<Return>', entry_callback)
        self._newtab_input.pack(side=tk.TOP, anchor=tk.S, fill=tk.Y, expand=True)
        self._newtab_input.focus_set()

    def create_tab(self, tabname):
        buttonframe = tk.Frame(self._topbar)
        button = Reactive(tk.Button(buttonframe, anchor=tk.W, text=tabname, command=lambda arg=tabname: self._on_button(arg)))
        underline = tk.Frame(buttonframe, height=1, background = self.option_get('foreground','Foreground'))
        button.pack(side=tk.TOP, fill=tk.X, expand=True)
        underline.pack(side=tk.BOTTOM, anchor=tk.S, fill=tk.X, expand=True)
        self._tabs[tabname] = (tk.Frame(self), underline, button)
        buttonframe.pack(side=tk.LEFT, anchor=tk.NW, fill=tk.BOTH, expand=True)

        if len(self._tabs) == 1:
            self._on_button(tuple(self._tabs.keys())[0])
        
        return self._tabs[tabname][0]

    def tab_frames(self):
        return [t[0] for t in self._tabs.values()]

    def tab_frame(self, tabname: str):
        return self._tabs[tabname][0]

    def tabs(self):
        return [t for t in self._tabs.keys()]
