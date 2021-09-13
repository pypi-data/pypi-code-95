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
commonly used functions
"""

from pathlib import Path

from pyprojstencil.configure import PyConfig


def edit_modify(text: str, config: PyConfig) -> str:
    """
    Insert modifications in the text based on configuration

    Args:
        text: text to modify
        config: configuration to use

    Returns:
        modified text
    """
    for key in config.keys:  # CANT: use __dict__ because uname is a @property
        value = getattr(config, key)
        if value is None:
            continue
        if isinstance(value, Path):
            text = text.replace(f'<{key.upper()}>', value.name)
        else:
            text = text.replace(f'<{key.upper()}>', value)
    return text
