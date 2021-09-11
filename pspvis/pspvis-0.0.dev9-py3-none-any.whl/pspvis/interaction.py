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
Interactive message boxes, dialog boxes, etc
"""

import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import TclError, ttk
from typing import Any, Dict, List, Union

from pspvis import AVAIL_THEMES, __version__, _name
from pspvis.data_types import PlotUserVars
from pspvis.preferences import write_config

ANNOT_FILES = (('yaml files', '*.yml *.yaml'), ('toml files', '*.toml'),
               ('conf files', '*.conf *.cfg'))
SHEET_FILES = (('spreadsheet files', '*.csv *.tsv'), )


class PlotProgress(tk.Toplevel):
    """
    Indeterminate progress bar for plot progress
    """
    def __init__(self, *args, title: str = _name, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = self.master
        self.mask: List[Union[tk.Widget, ttk.Widget]] = []
        try:
            self.attributes('-type', 'dialog')
        except TclError:
            pass
        self.title(_name + ': ' + title)
        self.progress = ttk.Progressbar(master=self,
                                        length=300,
                                        mode='indeterminate',
                                        orient='horizontal')
        self.ready = ttk.Label(master=self)

        self.progress.grid(row=1, column=0, columnspan=10, sticky=tk.NSEW)
        self.ready.grid(row=10, column=4, columnspan=2, sticky=tk.NSEW)

        self.grid_columnconfigure(4, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def busy(self, mask: List[Union[tk.Widget, ttk.Widget]] = None):
        self.mask = mask or []
        for widget in self.mask:
            try:
                widget.config(state='disabled')
            except TclError:
                self.mask.pop(self.mask.index(widget))
        self.ready.config(text='working...')
        self.progress.start()

    def done(self):
        self.ready.config(text='done')
        for widget in self.mask:
            try:
                widget.config(state='normal')
            except TclError:
                pass
        self.mask = []
        self.progress.stop()
        self.destroy()


class PopUp(tk.Toplevel):
    '''
    Toplevel popup dialog with customizable contents

    Available grids:
        rows: 1 through 9
        columns: 0 through 10
        flex-columns: 4,6
    '''
    def __init__(self, *args, popup_kwargs: Dict[str, Any] = None, **kwargs):
        super().__init__(*args, **kwargs)
        popup_kwargs = popup_kwargs or {}
        self.title(popup_kwargs.get('title', _name))
        try:
            self.attributes('-type', 'dialog')
        except TclError:
            pass
        # OK button
        spacer = ttk.Separator(self, orient='horizontal')
        spacer.grid(row=10, column=0, columnspan=10, sticky=tk.NS)
        ok_btn = ttk.Button(self, text='OK', command=self.ok_cmd)
        ok_btn.grid(row=11,
                    column=4,
                    columnspan=2,
                    padx=10,
                    pady=5,
                    sticky=tk.NS)
        if popup_kwargs.get('cancel', False):
            cancel_btn = ttk.Button(self, text='CANCEL', command=self.destroy)
            cancel_btn.grid(row=11,
                            column=6,
                            columnspan=2,
                            padx=10,
                            pady=5,
                            sticky=tk.NS)
            self.grid_columnconfigure(6, weight=1)
        self.grid_rowconfigure(10, weight=1)
        self.grid_columnconfigure(4, weight=1)
        self.bind('<Return>', self.ok_cmd)
        self.bind('<Escape>', self.cancel)

    def ok_cmd(self, *_):
        self.cancel()

    def cancel(self, *_):
        self.destroy()


class CsvDialog(PopUp):
    """
    Dialog to import csv file
    """
    def __init__(self, *args, csv_kwargs: Dict[str, Any] = None, **kwargs):
        csv_kwargs = csv_kwargs or {}
        super().__init__(popup_kwargs={'title': 'CSV import'}, *args, **kwargs)
        self.ui = self.master

        self.sep_group = self.create_sep(csv_kwargs['sep'])
        self.sep_group['label'].grid(row=1, column=3, padx=10, pady=10)
        self.sep_group['entry'].grid(row=1, column=4, padx=10, pady=10)

        self.column_group = self.create_column(csv_kwargs.get('row0', []))
        self.column_group['label'].grid(row=2, column=3, padx=10, pady=10)
        self.column_group['entry'].grid(row=2, column=4, padx=10, pady=10)

        self.row_group = self.create_row(csv_kwargs.get('col0', []))
        self.row_group['label'].grid(row=3, column=3, padx=10, pady=10)
        self.row_group['entry'].grid(row=3, column=4, padx=10, pady=10)

    def show(self):
        self.deiconify()
        self.wait_window()
        sep = self.sep_group['var'].replace('\t', '\\t')
        index_col = [None, 0][self.is_col]
        header = [None, 0][self.is_row]
        return {'sep': sep, 'index_col': index_col, 'header': header}

    def create_sep(self, sep=','):
        label = ttk.Label(master=self, text='column-separator')
        sep_entry = tk.Entry(master=self, width=5)
        sep_entry.insert(0, sep)
        return {'label': label, 'entry': sep_entry, 'var': sep_entry.get()}

    def create_column(self, seen_vals: List[str]):
        self.is_col: bool = True
        label_opt = ['These are column VALUES', 'These are column NAMES']
        tk_disp = tk.StringVar(self, label_opt[int(self.is_col)])

        def toggle_text(*_):
            self.is_col = not self.is_col
            tk_disp.set(label_opt[self.is_col])

        tk_col_text = ttk.Label(self,
                                textvariable=tk_disp,
                                foreground='#44f',
                                cursor='hand2')
        tk_col_text.bind('<Button-1>', toggle_text)
        tk_col_text.bind('<Return>', toggle_text)
        tk_list = ttk.Label(self, text=', '.join(seen_vals))

        return {'label': tk_list, 'entry': tk_col_text}

    def create_row(self, seen_vals: List[str]):
        self.is_row: bool = True
        label_opt = ['These are row VALUES', 'These are row NAMES']
        tk_disp = tk.StringVar(self, label_opt[int(self.is_row)])

        def toggle_text(*_):
            self.is_row = not self.is_row
            tk_disp.set(label_opt[self.is_row])

        tk_row_text = ttk.Label(self,
                                textvariable=tk_disp,
                                foreground='#44f',
                                cursor='hand2')
        tk_row_text.bind('<Button-1>', toggle_text)
        tk_row_text.bind('<Return>', toggle_text)
        tk_list = ttk.Label(self, text=', '.join(seen_vals))

        return {'label': tk_list, 'entry': tk_row_text}


class PrefMod(PopUp):
    def __init__(self, *args, conf: PlotUserVars = None, **kwargs):

        # copy from conf
        self.conf = PlotUserVars()
        self.conf.update(conf)

        # option ranges
        self.ui_themes = AVAIL_THEMES['ui']
        self.mpl_themes = AVAIL_THEMES['mpl']
        self.spot_size_range = 0, 300

        popup_kwargs = {
            'title': f'{_name} Preferences',
            'cancel': True,
        }
        super().__init__(popup_kwargs=popup_kwargs, *args, **kwargs)

        self.ui = self.master

        self.tk_ui_theme = tk.StringVar(self)
        self.tk_mpl_theme = tk.StringVar(self)
        self.tk_hold_annot = tk.IntVar(self, value=self.conf.hold_annot)

        self.hold_btn = ttk.Checkbutton(self,
                                        text='Hold annotation mode',
                                        variable=self.tk_hold_annot)
        self.spot_spin = ttk.Spinbox(self,
                                     from_=self.spot_size_range[0],
                                     to=self.spot_size_range[1])
        self.spot_spin.set(self.conf.spot_size)

        self._display()

    def ok_cmd(self, *_):
        """
        callback on 'OK'
        """
        self._update_vars()
        write_config(self.conf)
        self.ui.plot.user_vars.update(self.conf)
        self.destroy()
        self.ui.plot.refresh_scatter()

    def _display(self):
        "Show preferences dialog"

        ui_drop_label = ttk.Label(self, text='Interface Theme')
        mpl_drop_label = ttk.Label(self, text='Plot Theme')
        spot_label = ttk.Label(self, text='Spot size')

        ui_opts = list(self.ui_themes.keys())
        mpl_opts = list(self.mpl_themes.keys())

        ui_drop = ttk.OptionMenu(
            self,
            self.tk_ui_theme,
            self.conf.ui_theme,
            command=lambda *_: self.ui.set_ui_theme(self.tk_ui_theme.get()),
            *ui_opts)

        mpl_drop = ttk.OptionMenu(self, self.tk_mpl_theme, self.conf.mpl_theme,
                                  *mpl_opts)

        self.tk_ui_theme.set(self.conf.ui_theme)
        self.tk_mpl_theme.set(self.conf.mpl_theme)

        spot_label.grid(row=1, column=4)
        self.spot_spin.grid(row=1, column=5)

        ui_drop_label.grid(row=2, column=4)
        ui_drop.grid(row=2, column=5)

        mpl_drop_label.grid(row=3, column=4)
        mpl_drop.grid(row=3, column=5)

        self.hold_btn.grid(row=4, column=5)

    def _update_vars(self, *_):
        """
        Bind StrVars to PlotUserVars
        """
        self.conf.ui_theme = self.tk_ui_theme.get()
        self.conf.mpl_theme = self.tk_mpl_theme.get()
        self.conf.spot_size = min(max(int(self.spot_spin.get()), 1), 300)
        self.ui.tool_bar.user_vars['spot_size'].set(self.conf.spot_size)
        self.conf.hold_annot = bool(self.tk_hold_annot.get())


def pref_mod(master, conf: PlotUserVars = None):
    """
    Construct Preferences Dialog
    """
    preferences = PrefMod(master, conf=conf)
    master.wait_window(preferences)


def info(master):
    "Show info message"
    ext_links = {
        'source-code': 'https://gitlab.com/pradyparanjpe/pspvis.git',
        'readthedocs': 'https://pradyparanjpe.gitlab.io/pspvis',
        'pip': 'https://pypi.org/project/pspvis',
        'license': 'https://www.gnu.org/licenses/lgpl-3.0.html'
    }
    message = PopUp(master,
                    popup_kwargs={'title': f'About {_name} {__version__}'})
    l_index = 0
    link_f = ttk.Frame(message)
    link_f.grid(row=1, column=0, columnspan=10, sticky=tk.NS, padx=40, pady=80)
    for text, url in ext_links.items():
        l_index += 1
        link_label = ttk.Label(link_f,
                               text=f'{l_index}. {text}',
                               font=('Sans', 14, 'bold'),
                               foreground='#33f',
                               cursor='hand2')
        link_label.bind('<Button-1>',
                        lambda *_, url=url: webbrowser.open_new_tab(url))
        link_label.grid(row=l_index, sticky=tk.NSEW)
    master.wait_window(message)


def ask_csv_attr(master, filepath: Path):
    """
    Ask for csv parser attributes

    Args:
        master: master frame
        filepath: csv filepath

    Returns:
        Attributes dict with keys:
            - sep
            - col_index
            - headers

    """
    sep = {'.tsv': '\t', '.csv': ','}.get(filepath.suffix, '')
    csv_kwargs: Dict[str, Any] = {}

    csv_kwargs['col0'] = []
    with open(filepath) as csv_h:
        csv_kwargs['row0'] = csv_h.readline().rstrip().split(sep)[:10]
    with open(filepath) as csv_h:
        count_lines = 0
        for line in csv_h.readlines():
            count_lines += 1
            csv_kwargs['col0'].append(line.split(sep)[0][:10])
            if count_lines >= 5:
                break

    csv_kwargs['sep'] = sep.replace('\t', '\\t')
    return CsvDialog(master=master, csv_kwargs=csv_kwargs).show()
