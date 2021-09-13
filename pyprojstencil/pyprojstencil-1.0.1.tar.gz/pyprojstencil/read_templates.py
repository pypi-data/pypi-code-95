#!/usr/bin/env python3
# -*- coding:utf-8; mode:python; -*-
#
# Copyright 2021 Pradyumna Paranjape
# This file is part of pyprojstencil.
#
# pyprojstencil is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyprojstencil is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pyprojstencil.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Read templates
"""

from pathlib import Path
from typing import List, Tuple


class InfoBase:
    """
    InfoBase to construct the project

    Attributes:
        licenses: list of license paths

    """
    def __init__(self):
        self._root = Path(__file__).parent
        self.templates = self._root.joinpath('templates')
        self.licenses: List[Tuple[Path, Path]] = []

    def _get_licenses(self):
        """
        parse known licenses
        """
        headers: List[Path] = []
        licenses: List[Path] = []
        for text_file in self.templates.joinpath('licenses').glob('*'):
            if not text_file.is_file():
                continue
            if text_file.stem[-7:] == '_header':
                headers.append(text_file)
            else:
                licenses.append(text_file)
        for header_path in headers:
            license_path = str(header_path).replace('_header', '')
            if license_path in licenses:
                self.licenses.append((header_path, license_path))


INFO_BASE = InfoBase()
"""
Database-like Object that contains all necessary template information
"""
