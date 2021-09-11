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
Shared data types
"""

from dataclasses import dataclass
from typing import Any, Callable, ItemsView, Union


@dataclass
class PlotUserVars():
    spot_size: int = 50
    hold_annot: bool = False
    mpl_theme: str = 'default'
    ui_theme: str = 'default'

    def update(self, template: Union['PlotUserVars', dict] = None):
        if template is None:
            return
        for attr, val in template.items():
            setattr(self, attr, val)

    def items(self) -> ItemsView[str, Any]:
        return self.__dict__.items()


class UiComm():
    """
    Object that UI will use to call pre-defined functions on parent
    """
    def __init__(self, **kwargs: Callable):
        """
        Communication pipe to UI

        Args:
            parent: parents's callable functions will be called

        """
        for name, call in kwargs.items():
            self.add_callback(name, call)

    def add_callback(self, attr_name: str, call: Callable):
        setattr(self, attr_name, call)

    def rem_callback(self, attr_name):
        delattr(self, attr_name)
