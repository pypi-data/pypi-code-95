#!/usr/bin/env python3
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
PCA-assisted Spreadsheet Plot Visualization
"""


from pspvis.preferences import collect_themes, read_config

__version__ = "0!0.0dev9"

_name = 'PspVis'

USER_VARS = read_config()
"""
Preferences loaded from standard configuration locations
"""

AVAIL_THEMES = collect_themes()
"""
Available themes on the platform (for ui and matplotlib)
"""

from pspvis.plot import PcaVis

__all__ = ['_name', '__version__', 'PcaVis', 'ICON_DIR']
