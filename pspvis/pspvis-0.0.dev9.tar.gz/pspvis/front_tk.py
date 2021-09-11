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
Frontend ttkinter UI

"""

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, List, Union

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from ttkthemes import ThemedTk

from pspvis import USER_VARS, _name
from pspvis.interaction import PlotProgress, ask_csv_attr, info, pref_mod
from pspvis.menu import PlotMenu
from pspvis.plot import PcaVis
from pspvis.toolbar import ToolBar

ANNOT_FILES = (('yaml files', '*.yml *.yaml'), ('toml files', '*.toml'),
               ('conf files', '*.conf *.cfg'))
SHEET_FILES = (('spreadsheet files', '*.csv *.tsv'), )


class MPLWidget(ttk.Frame):
    """
    Central Matplotlib widget, embeded with:
    - FigureCanvasTTKAgg (matplotlib figure canvas)
    - NavigationToolbar2TTK (matplotlib toolbar)

    Args:
        fig: matplotlab.Figure
        *args: all are passed to QWidget init
        *kwargs: all are passed to QWidget init
    Attributes:
        mpl_fig: mpl figure canvas
        mpl_tools: Navigation Toolbar
    """
    def __init__(self, fig, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.mpl_fig = FigureCanvasTkAgg(fig, self)
        self.mpl_fig.draw()
        self.mpl_tools = NavigationToolbar2Tk(self.mpl_fig, self)
        self.mpl_tools.update()
        self.mpl_fig.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


class TkUI(ThemedTk):
    """
    UI wrapping around matplotlib

    Args:
        *args: all are passed to QWidget init
        *kwargs: all are passed to QWidget init

    Attributes:
        central: Central Widget wrapper
        plot: matplotlib plot
        tool_bar: ToolBar
        mpl_display: MPLWidget (stretched)

    """
    def __init__(self, sheet: Path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # init objects
        self.style = ttk.Style(self)
        self.title(_name)
        self.set_plot()
        self.option_add('*tearOff', False)
        self.menu = PlotMenu(self)
        self['menu'] = self.menu
        self._set_shortcuts()
        self.iconphoto(
            False,
            tk.PhotoImage(file=Path(__file__).parent / 'icons/stars.png'))
        self.set_ui_theme(USER_VARS.ui_theme)
        if sheet is not None:
            self.load_sheet(sheet)

    def set_ui_theme(self, theme: str = 'default'):
        """
        Set theme for ui

        Args:
            theme: theme-name
        """
        if theme not in self.style.theme_names():
            # failsafe
            theme = 'default'
        self.style.theme_use(theme)

    def set_mpl_theme(self, theme: str = 'default'):
        """
        Set style for matplotlib.style.use

        Args:
            theme: theme-name
        """
        if theme not in self.plot.plt.style.available:
            # failsafe
            theme = 'default'
        self.plot.user_vars.mpl_theme = theme
        self.refresh_plot()

    def set_plot(self, **settings: Any):
        """
        Draw plot, optionally inheriting some data

        Args:
            dim: plot dimensions
            settings: inheritance settings for PcaVisualization
            **kwargs: update settings
        """
        self.plot = PcaVis(ui=self, **settings)
        # Possibly Long calculation
        self.tool_bar = ToolBar(self, self.plot.ui_comm)
        self.blocking_progress(title='refreshing plot',
                               mask=self.tool_bar.winfo_children(),
                               target=self.plot.refresh_scatter)
        self.mpl_display = MPLWidget(self.plot.fig, self)
        self.tool_bar.grid(row=1, column=0, sticky=tk.NSEW)
        self.mpl_display.grid(row=10, column=0, sticky=tk.NSEW)
        self.grid_rowconfigure(10, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def blocking_progress(self,
                          title: str = _name,
                          mask: List[Union[tk.Widget, ttk.Widget]] = [],
                          *args,
                          **kwargs):
        """
        show progress bar and monitor background process

        Args:
            title: title of progress-frame
            mask: disable these widgets
            *args: all are passed to threading .thread
            **kwargs: all are passed to threading .thread
        """
        progress = PlotProgress(self, title=title)
        thread = threading.Thread(*args, **kwargs, daemon=True)
        progress.busy(mask)
        thread.start()
        self.monitor_progress(thread, progress)

    def refresh_plot(self, inherit: bool = True, **kwargs):
        """
        Refresh central widget
        Args:
            dim: plot dimensions
            **kwargs: passed to set_plot
        """
        settings = self.plot.extract_settings() if inherit else {}
        settings.update(kwargs)
        for frame in self.winfo_children():
            if frame is not self.menu:
                frame.destroy()
        self.set_plot(**settings)
        self.menu.update_schemes()

    def load_sheet(self, filepath: Path = None, annotation: bool = True):
        """
        Select a data-csv spreadsheet file to load data.
        If an annotation file with the same name-stem is found, offer to use it

        Args:
            filepath: load from filepath (else select from Dialog)
            annotation: look if annotation file is available.

        """
        if filepath is None:
            query = filedialog.askopenfilename(title='Load spreadsheet',
                                               parent=self,
                                               filetypes=SHEET_FILES)
            if not query:
                return
            filepath = Path(query)
        if not filepath.is_file():
            self.throw(f"couldn't locate {filepath}", type=FileNotFoundError)
            return

        table_attrs = ask_csv_attr(self, filepath)
        self.blocking_progress(target=self.plot.ui_comm.load_sheet,
                               args=(filepath, ),
                               kwargs=table_attrs,
                               title='Loading Data',
                               mask=self.tool_bar.winfo_children())
        if annotation:
            for conf_file_suffix in ('.yml', '.yaml', '.toml', '.conf',
                                     '.cfg'):
                found_annot = filepath.with_suffix(conf_file_suffix)
                if found_annot.is_file():
                    reply = messagebox.askyesno(
                        parent=self,
                        title='Found Annotation',
                        message=f'Load annotation {found_annot}?')
                    if reply:
                        self.load_annot(found_annot, sheet=False)
                        break
        self.blocking_progress(title='refreshing plot',
                               mask=self.tool_bar.winfo_children(),
                               target=self.plot.refresh_scatter)

    def monitor_progress(self, proc: threading.Thread, progress):
        if proc.is_alive():
            self.after(100, lambda *_: self.monitor_progress(proc, progress))
        else:
            progress.done()

    def load_annot(self, filepath: Path = None, sheet: bool = True):
        """
        Select a data-csv spread sheet file to load data.
        If a sheet file with the same name-stem is found, offer to use it.

        Args:
            filepath: load from filepath (else select from Dialog)
            sheet: look if sheet file is available.

        """
        if filepath is None:
            query = filedialog.askopenfilename(parent=self,
                                               title='Load Annotation',
                                               filetypes=ANNOT_FILES)
            if not query:
                return None
            filepath = Path(query[0])
        if not filepath.is_file():
            return None
        if sheet and self.plot._sheet['raw'].empty:
            for sheet_file_suffix in ('.csv', '.tsv'):
                found_sheet = filepath.with_suffix(sheet_file_suffix)
                if found_sheet.is_file():
                    reply = messagebox.askyesno(
                        parent=self,
                        title='Found spreadsheet',
                        message=f'Load data {found_sheet}?')
                    if reply:
                        self.load_sheet(found_sheet, annotation=False)
                        break
        self.plot.ui_comm.load_annot(filepath)
        self.menu.update_schemes()

    def _spot_mod(self, increment: int = None):
        if increment is None:
            new_size = 50
        else:
            new_size = self.plot.user_vars.spot_size + increment
            if not (0 <= new_size <= 300):
                return
        self.tool_bar.user_vars['spot_size'].set(new_size)
        self.plot.user_vars.spot_size = new_size
        self.plot.refresh_scatter()

    def _set_shortcuts(self):
        """
        Bind shortcuts
        """
        # Control-
        self.bind('<Control-o>', lambda *_: self.load_sheet())
        self.bind('<Control-O>', lambda *_: self.load_annot())
        self.bind('<Control-w>', lambda *_: self.refresh_plot(inherit=False))
        self.bind('<Control-h>', lambda *_: info(self))
        self.bind('<Control-equal>', lambda *_: self._spot_mod(10))
        self.bind('<Control-plus>', lambda *_: self._spot_mod(10))
        self.bind('<Control-minus>', lambda *_: self._spot_mod(-10))
        self.bind('<Control-0>', lambda *_: self._spot_mod())
        self.bind('<Control-H>', self.tool_bar.toggle_hold)
        self.bind('<Control-f>',
                  lambda *_: self.tool_bar.find_field.focus_set())
        self.bind('<Control-m>', lambda *_: self.plot.ui_comm.clear_annot())

        self.bind('<Control-comma>',
                  lambda *_: pref_mod(self, self.plot.user_vars))
        self.bind('<F12>',
                  lambda *_: pref_mod(self, self.plot.user_vars))
        self.bind('<Return>', lambda *_: self.tool_bar.search())
        self.bind('<F5>', lambda *_: self.plot.refresh_scatter())
        self.protocol("WM_DELETE_WINDOW", self.quit)

    def throw(self, message, type):
        """
        Throw errors sent by plot as Error Message Box
        """
        messagebox.showerror(title=type, message=message, parent=self)
