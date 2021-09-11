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
Images for tk

"""

import tkinter as tk
from pathlib import Path


def collect_icons():
    """
    collect icons
    """
    icon_dir = Path(__file__).parent / 'icons'
    icons = {}
    icons['refresh'] = tk.PhotoImage(file=icon_dir / 'refresh-ccw.png')
    icons['search'] = tk.PhotoImage(file=icon_dir / 'search.png')
    icons['clear'] = tk.PhotoImage(file=icon_dir / 'x-circle.png')
    return icons
