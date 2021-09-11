#!/usr/bin/env python
# -*- coding: utf-8; mode: python; -*-
# Copyright © 2020-2021 Pradyumna Paranjape
#
# This file is part of pspvis.
#
# pspvis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pspvis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pspvis. If not, see <https://www.gnu.org/licenses/>.
#
"""
Top Toolbar

"""

import tkinter as tk
from tkinter import ttk

from pspvis import USER_VARS
from pspvis.data_types import UiComm
from pspvis.images import collect_icons


class HoverTip(object):
    """
    Hint displayed on mouse-enter-event
    """
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x, self.y = 0, 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw,
                         text=self.text,
                         justify=tk.LEFT,
                         background="#ffffe0",
                         foreground="#1f1f00",
                         relief=tk.SOLID,
                         borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def create_hover_hint(widget, text):
    toolTip = HoverTip(widget)

    def enter(*_):
        toolTip.showtip(text)

    def leave(*_):
        toolTip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


class ToolBar(ttk.Frame):
    """
    Tool Bar
    - a TextLine Field to insert text
    - a find button to trigger search
    - a "Hold spots" button
    - a slider controling spot-size
    - a regex radio button for passing 're' formatted text

    Args:
        comm: communication callable: with defs: 'clear_annot', 'search_spots'
        *args: all are passed to QWidget init
        *kwargs: all are passed to QWidget init

    Attributes:
        comm: communication callable
        ui: communication ui handle
        find_field: tk.Text to find spots
        user_vars: User-configurable variables: hold_annot, spot_size
    """
    def __init__(self, master: 'TkUI', comm: UiComm, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.ui = master
        self._re = tk.IntVar(value=0)
        self.comm = comm
        self.icons = collect_icons()

        # Labels
        spot_label = ttk.Label(self, text='spots:', font=('Sans', 14, 'bold'))
        annot_label = ttk.Label(self,
                                text='annotations:',
                                font=('Sans', 14, 'bold'))

        # Buttons
        self.user_vars = {
            'hold_annot': tk.IntVar(value=USER_VARS.hold_annot),
            'spot_size': tk.IntVar(value=USER_VARS.spot_size)
        }
        self.find_field = tk.Text(self, height=1, width=30)
        refresh_btn = ttk.Button(self,
                                 image=self.icons['refresh'],
                                 command=self.ui.plot.refresh_scatter)
        create_hover_hint(refresh_btn, 'Refresh Plot\n<F5>')
        re_check = ttk.Checkbutton(self, text='regexp', variable=self._re)
        create_hover_hint(re_check, 'Advanced usage')
        hold_annot = ttk.Checkbutton(self,
                                     text='Hold',
                                     variable=self.user_vars['hold_annot'],
                                     command=self.update_scatter_mod)
        create_hover_hint(hold_annot, 'Hold Annotations\n<Ctrl+Shift+H>')
        size_scale = ttk.Scale(self,
                               name='spot size',
                               orient=tk.HORIZONTAL,
                               from_=1,
                               to=300,
                               variable=self.user_vars['spot_size'],
                               command=self.update_refresh)
        create_hover_hint(size_scale, 'spot-size\n<Ctrl+plus>\n<Ctrl+minus>')
        size_scale.bind('<MouseWheel>', self.mouse_wheel)
        size_scale.bind('<Button-4>', self.mouse_wheel)
        size_scale.bind('<Button-5>', self.mouse_wheel)
        find_btn = ttk.Button(self,
                              image=self.icons['search'],
                              command=lambda *_: self.search())
        create_hover_hint(find_btn, 'find spots\n<Return>')
        clear_ann = ttk.Button(self,
                               image=self.icons['clear'],
                               command=lambda *_: self.comm.clear_annot())
        create_hover_hint(clear_ann, 'Clear Annotation\n<Ctrl+m>')
        spacer = ttk.Separator(master=self, orient=tk.HORIZONTAL)

        # Place
        spot_label.grid(sticky=tk.EW, row=1, column=0, padx=5)
        refresh_btn.grid(sticky=tk.EW, row=1, column=1, padx=5)
        self.find_field.grid(sticky=tk.EW, row=1, column=2, padx=5)
        find_btn.grid(sticky=tk.EW, row=1, column=3, padx=5)
        re_check.grid(sticky=tk.E, row=1, column=4, padx=5)
        annot_label.grid(sticky=tk.W, row=1, column=10, padx=5)
        size_scale.grid(sticky=tk.EW, row=1, column=11, padx=5)
        hold_annot.grid(sticky=tk.EW, row=1, column=12, padx=5)
        clear_ann.grid(sticky=tk.EW, row=1, column=13, padx=5)
        self.grid_columnconfigure(9, weight=5)
        self.grid_columnconfigure(2, weight=5)
        self.grid_columnconfigure(11, weight=5)

    def mouse_wheel(self, event):
        # respond to Linux or Windows wheel event
        increment = 0
        if event.num == 5 or event.delta == -120:
            increment = -10
        elif event.num == 4 or event.delta == 120:
            increment = 10
        mod = self.user_vars['spot_size'].get() + increment
        if not (0 <= mod <= 300):
            return
        self.user_vars['spot_size'].set(mod)
        self.update_scatter_mod()

    def toggle_hold(self, *_):
        self.user_vars['hold_annot'].set(
            ((self.user_vars['hold_annot'].get() + 1) % 2))
        self.update_scatter_mod()

    def update_refresh(self, *_):
        self.update_scatter_mod()
        self.refresh()

    def update_scatter_mod(self, *_):
        user_vars = {key: val.get() for key, val in self.user_vars.items()}
        self.ui.plot.user_vars.update(user_vars)

    def refresh(self, *_):
        self.ui.plot.refresh_scatter()

    def search(self):
        """
        Trigger communication with plot
        sends (rstripped) search-text
        - if re is checked, send raw, else:
        - * is converted to .* for regexp
        - .* is appended to acc_str for regexp
        search text entered: ``A*BCD``
        search text sent: ``A.*BCD.*``

        """
        search_text = self.find_field.get('1.0', 'end-1c').rstrip()
        if search_text:
            if self._re.get() == 0:
                # create re from entered text
                special_characters = ('?', '.', '+', '(', ')', '[', ']', '{',
                                      '}', '^', '$', '\\')
                for char in special_characters:
                    search_text = search_text.replace(char, '\\' + char)
                search_text = search_text.replace('*', '.*') + '.*'
            self.comm.search_spots(search_text)
            self.find_field.delete('1.0', 'end-1c')
