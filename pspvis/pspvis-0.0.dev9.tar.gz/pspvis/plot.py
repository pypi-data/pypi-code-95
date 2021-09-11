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
plot
"""

import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backend_bases import MouseEvent
from matplotlib.collections import PathCollection
from matplotlib.text import Annotation
from mpl_toolkits import mplot3d as plt3d
from psprint import print
from sklearn.decomposition import PCA

from pspvis import USER_VARS
from pspvis.annotation import DataAnnot
from pspvis.data_types import PlotUserVars, UiComm
from pspvis.errors import MatchOverFlow, VisKeyError
from pspvis.read_config import load_configuration

BBOX = {'boxstyle': 'round', 'alpha': 0.4}
ARROWPROPS = {'arrowstyle': '->'}


def pca_transform(raw: pd.DataFrame, n_comp: int = 2) -> pd.DataFrame:
    """
    extract principal components of rawentration

    Args:
        raw: all x: comps' and y: phases
        n_comp: number of components to return

    """
    pca_worker = PCA(n_components=n_comp)
    principal_comps_n = pd.DataFrame(
        pca_worker.fit_transform(raw),
        columns=list(comp for comp in range(n_comp))).set_index(raw.index)
    assert isinstance(principal_comps_n, pd.DataFrame)
    col_names = {
        idx: f'explained variance: {val*100:.4g}%'
        for idx, val in enumerate(pca_worker.explained_variance_ratio_)
    }
    return principal_comps_n.rename(columns=col_names)


class Annotation3D(Annotation):
    """
    Annotation for 3D axes

    Args:
        text: text to display as annotation
        xyz: annotation co-ordinates
        *args: passed to `matplotlib.text.Annotation`
        **kwargs: passed to `matplotlib.text.Annotation`
    """
    def __init__(self, text: str, xyz: Tuple[float, float, float], *args,
                 **kwargs):
        Annotation.__init__(self, text, xy=(0, 0), *args, **kwargs)

        # 3D position
        self._xyz = xyz

        # Hard-set 2D projection
        self._xy: Optional[Tuple[float, float]] = None

    @property
    def xy(self):
        if self._xy is not None:
            return self._xy
        *xy2d, _ = plt3d.proj3d.proj_transform(*self._xyz, self.axes.M)
        return xy2d

    @xy.setter
    def xy(self, val):

        # Hard-set
        self._xy = val

    @xy.deleter
    def xy(self):
        # Unset
        self._xy = None


def annotateND(ax: Union[plt.Axes, plt3d.axes3d.Axes3D], text: str,
               xyz: Tuple[float, float, float], *args, **kwargs):
    """
    Add annotation to 3D axes

    Args:
        ax: target (parent) axes
        text: Annotation text
        xyz: annotation co-ordinates
        *args: passed to `matplotlib.text.Annotation`
        **kwargs: passed to `matplotlib.text.Annotation`

    Returns:
        Annotation3D artist object
    """

    if isinstance(ax, plt3d.axes3d.Axes3D):
        a = Annotation3D(text, xyz, *args, **kwargs)
        ax.add_artist(a)
        return a
    return ax.annotate(text, xyz, *args, **kwargs)


class PcaVis(object):
    """
    PCA Visualization Container

    Attributes:
        ui: graphics UI, must define a function 'throw' to send errors
        dim: dimensions
        plt, fig: matplotlib plot, figure
        cg_hl: handle for currently shown centroids
        spot_vis_d: spot annotation handles
        table: table in current view (raw or pca transformed)
        data_annot: annotation schemes
        scheme: currnet scheme
        mpl_theme: matplotlib style to use

    Args:
        ui: parent graphics ui
        dim: 2/3 dimensions
        settings: settings to inherit
    """
    def __init__(self, ui=None, **settings: Any) -> None:
        # Inherited attributes:
        self._sheet: Dict[str, pd.DataFrame] = {
            'pca': pd.DataFrame(),
            'transpose': pd.DataFrame(),
            'transpose_pca': pd.DataFrame(),
            'raw': settings.get('raw_sheet', pd.DataFrame())
        }
        self.data_annot: DataAnnot = settings.get('data_annot', DataAnnot())
        self.scheme: str = settings.get('scheme', 'None')
        self.user_vars = USER_VARS
        self.user_vars.update(settings.get('user_vars'))
        self.dim = settings.get('dim', 2)
        self.projection = settings.get('projection', 'raw')

        # Own attributes
        self._lock = []
        self.spot_vis_d: Dict[Union[str, int],
                              Dict[Union[str],
                                   Tuple[PathCollection,
                                         Union[Annotation,
                                               Annotation3D]]]] = {}
        self.cg_hl: Dict[Union[str, int], Tuple[PathCollection,
                                                Union[Annotation,
                                                      Annotation3D]]] = {}
        self._spot_orig_colors = {}
        self.ui = ui
        self.plt = plt
        self.plt.style.use(self.user_vars.mpl_theme)
        self.fig = self.plt.figure()
        self.sc_ax: Union[plt3d.axes3d.Axes3D,
                          plt.Axes] = self.fig.add_subplot(
                              projection='3d' if self.dim == 3 else None)

        self._resize_raw_sheet()
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.ui_comm = UiComm(
            load_sheet=self.load_sheet,
            load_annot=self.load_annot,
            apply_scheme=self.apply_scheme,
            search_spots=self.search_spots,
            clear_annot=self.clear_annot,
            proj=self.proj,
        )

        return

    def clear_annot(self):
        """
        Remove highlights
        """
        # remove previously highlighted spots
        for cg in self.cg_hl.values():
            cg[0].remove()
            cg[1].remove()
        # flush
        self.cg_hl = {}

        # reset colors of group
        for spot, spot_color in self._spot_orig_colors.items():
            spot.set_facecolor(spot_color)
        self._spot_orig_colors = {}

        # set all annotations invisible
        for group in self.spot_vis_d.values():
            for spot in group.values():
                spot[1].set_visible(False)
        self.fig.canvas.draw_idle()

    def _resize_raw_sheet(self):
        """
        If raw sheet has less than n_dim columns, add sufficient zero columns
        """
        zero_cols = self.dim - self._sheet['raw'].shape[1]
        for zcol in range(zero_cols):
            self._sheet['raw'][f'zero_{zcol}'] = 0

    def extract_settings(self) -> Dict[str, Any]:
        """
        Extract settings for inheritance
        """
        settings = {}
        for attr in ('dim', 'data_annot', 'scheme', 'user_vars', 'projection',
                     'spot_vis_d', 'cg_hl'):
            settings[attr] = getattr(self, attr, None)
        settings['raw_sheet'] = self._sheet['raw']
        settings['cg_hl'] = {gid: None for gid in settings['cg_hl']}
        return settings

    def load_sheet(self, filename: Optional[Path], **table_attrs):
        """
        Load spread sheet

        Blocking function, needs lock

        Args:
            filename: load data co-ordinates from this file
            sep: spread sheet columns-separator

        """
        if filename is None:
            return

        if 'load_sheet' in self._lock:
            # another thread is working
            return
        self._lock.append('load_sheet')

        sep = table_attrs.get('sep', '')
        sep = {'tab': '\t', '\\t': '\t'}.get(sep.lower(), sep)
        sheet = pd.read_csv(Path(filename),
                            sep=sep,
                            header=table_attrs.get('header', 'infer'),
                            index_col=table_attrs.get('index_col'))
        assert isinstance(sheet, pd.DataFrame)
        self._sheet['raw'] = sheet
        # flush pca transformed data
        self._sheet['pca'] = pd.DataFrame()
        self._sheet['transpose'] = pd.DataFrame()
        self._sheet['pca_transpose'] = pd.DataFrame()
        self._resize_raw_sheet()
        self.data_annot.rows = {
            **({idx: ''
                for idx in list(self._sheet['raw'].index)}),
            **self.data_annot.rows
        }
        self.data_annot.cols = {
            **({idx: ''
                for idx in list(self._sheet['raw'].columns)}),
            **self.data_annot.cols
        }
        self._lock.pop(self._lock.index('load_sheet'))

    def load_annot(self, filename: Optional[Path] = None):
        """
        Load annotation confituration

        Args:
            filename: Load annotations from this file
        """
        if filename is None:
            return
        self.data_annot.update(load_configuration(Path(filename)))
        # self.data_annot.filter(self._sheet['raw'])

    def transform(self):
        """
        extract principal components of columns

        """
        if self.projection == 'pca':
            self._sheet[self.projection] = pca_transform(
                self._sheet['raw'], self.dim)
            return

        if self.projection == 'transpose':
            self._sheet[self.projection] = self._sheet['raw'].transpose()
        elif self.projection == 'transpose_pca':
            self._sheet[self.projection] = pca_transform(
                self._sheet['raw'].transpose(), self.dim)
        self.scheme = 'None'

    def proj(self, projection: str = 'raw'):
        """
        Switch plot between truncated columns and PCA projection

        Args:
            pca: ?project PCA?
        """
        if projection == self.projection:
            return
        self.projection = projection
        self.refresh_scatter()

    def apply_scheme(self, scheme: str):
        """
        Apply grouping scheme
        Args:
            scheme: scheme
        """
        print(f'Updated scheme: {scheme}', mark=2)
        self.scheme = scheme
        self.refresh_scatter()

    def annotate_group(self, table: pd.DataFrame, gid: Union[str, int], color):
        """
        Annotate all points in group

        Args:
            group: group name
            color: hsv color scheme to be used
        """
        scheme = self.data_annot.schemes[self.scheme]
        grp_in_tbl = list(filter(lambda x: x in table.index, scheme[gid]))
        if not grp_in_tbl:
            return
        group = table.loc[grp_in_tbl].iloc[:, :self.dim]
        self.spot_vis_d[gid] = {}
        for spot_idx, spot in zip(group.index, group.values):
            data_sc: PathCollection = self.sc_ax.scatter(
                *spot, s=self.user_vars.spot_size, c=[color], alpha=0.5)
            text: str = str(spot_idx) + ': ' + str(
                self.data_annot.rows.get(spot_idx, '')[:30]) + str(
                    self.data_annot.cols.get(spot_idx, '')[:30])
            spot_annot = annotateND(self.sc_ax,
                                    text,
                                    spot,
                                    xytext=(20, 20),
                                    textcoords='offset points',
                                    bbox=BBOX,
                                    arrowprops=ARROWPROPS)
            spot_annot.set_visible(False)
            self.spot_vis_d[gid][spot_idx] = (data_sc, spot_annot)

    def refresh_scatter(self, user_vars: PlotUserVars = None):
        """
        Update scatter

        Blocking Processing function, needs a lock

        Args:
            user_vars: user-modified plot variables

        """
        if 0 in self._sheet['raw'].shape:
            return

        if 'refresh_scatter' in self._lock:
            return
        self._lock.append('refresh_scatter')

        if user_vars:
            self.user_vars.update(user_vars)

        if self.projection != 'raw' and self._sheet[self.projection].empty:
            # lazy
            self.transform()

        table = self._sheet[self.projection]

        # erase scatter
        self.sc_ax.clear()
        self.spot_vis_d = {}

        grp_count = 0
        scheme = self.data_annot.schemes[self.scheme]
        for gid in scheme:
            color = self.plt.cm.hsv(grp_count / len(scheme))
            self.annotate_group(table, gid, color)
            grp_count += 1
        self.sc_ax.set_xlabel(f'{table.columns[0]}')
        self.sc_ax.set_ylabel(f'{table.columns[1]}')
        self.sc_ax.grid(linestyle=':')
        if isinstance(self.sc_ax, plt3d.axes3d.Axes3D):
            self.sc_ax.set_zlabel(f'{table.columns[2]}')
        else:
            self.sc_ax.set_aspect('equal')
        self.fig.canvas.draw_idle()
        self._lock.pop(self._lock.index('refresh_scatter'))

    def on_click(self, event: MouseEvent):
        """
        Trigger update_annotate for each group under the click event
        * bind to button-press-event on figure.canvas

        Args:
            event: mouse event

        """
        if event.inaxes == self.sc_ax:

            if not self.user_vars.hold_annot:
                self.clear_annot()

            for gid, spot_collection in self.spot_vis_d.items():
                for spot_sc in spot_collection.values():
                    vis = spot_sc[1].get_visible()
                    cont, _ = spot_sc[0].contains(event)
                    if cont:
                        spot_sc[1].set_visible(True)
                        if not vis:
                            self.mark_grp_cg(gid)

            self.fig.canvas.draw_idle()
        return

    def mark_grp_cg(self, gid: Union[str, int]) -> None:
        """
        Interactive annotation update

        - Click on a spot:
          - marks the spot's name
          - highlights group of the spot
          - marks centroid of the group

        - Click on empty space:
          - clears annotation marks

        Args:
           ind: itemlist returned by collections.PathCollection.contains(event)
           idx: spot-index in current-scheme

        """
        if gid in self.cg_hl:
            # already showing
            return
        table = self._sheet[self.projection]
        siblings = self.data_annot[self.scheme, gid]
        if len(siblings) == 1:
            # only one member
            return
        for spot_idx in siblings:
            assert (isinstance(spot_idx, str))
            spot = self.spot_vis_d[gid][spot_idx]
            spot_color = spot[0].get_facecolor()
            spot[0].set_facecolor("#7f7f7fff")
            self._spot_orig_colors[spot[0]] = spot_color
        cg = table.loc[siblings].mean(axis=0)[:self.dim].values
        cg_handle = self.sc_ax.scatter(*cg, s=5)
        cg_annot = annotateND(self.sc_ax,
                              f'Centroid of\n{gid}',
                              cg,
                              xytext=(-40, -40),
                              textcoords='offset points',
                              bbox=BBOX,
                              arrowprops=ARROWPROPS)
        self.cg_hl[gid] = cg_handle, cg_annot

    def search_spots(self, acc_str: str = ''):
        """
        Search and highlight spots with accession

        Args:
            acc_str: regular expression text (case ignored)

        """
        # remove all spot annotations
        if not self.user_vars.hold_annot:
            for group in self.spot_vis_d.values():
                for ann in group.values():
                    ann[1].set_visible(False)

        if not acc_str:
            return

        table = self._sheet[self.projection]

        acc_pat = re.compile(f'^{acc_str}', flags=re.IGNORECASE)
        acc_found = False
        matches: int = 0
        num_matches = 0
        for spot_idx, _ in table.iterrows():
            assert isinstance(spot_idx, (int, str))
            if num_matches > 50:
                # overflow
                if self.ui is not None:
                    self.ui.throw('Too many matching data accessions',
                                  type=MatchOverFlow)
                else:
                    print('Too many matching data accessions', mark='err')
                break
            if any(
                    acc_pat.match(str(text))
                    for text in (spot_idx,
                                 self.data_annot.get(spot_idx, [''])[0])):
                num_matches += 1
                matches += 1
                gid = self.data_annot[self.scheme, spot_idx][0]
                annotation = self.spot_vis_d[gid][spot_idx][1]
                if not annotation.get_visible():
                    annotation.set_visible(True)
        if matches:
            acc_found = True

        if not acc_found:
            if self.ui is not None:
                self.ui.throw('Not Found', type=VisKeyError)
            else:
                print('Not Found', mark='err')

        self.fig.canvas.draw_idle()
        return
