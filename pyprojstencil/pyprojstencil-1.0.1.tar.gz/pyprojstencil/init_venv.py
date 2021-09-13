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
Initialize git repository with ``pagan`` branch

``master`` this can be derived later from pagan by
trimming all unnecessary history
"""

from virtualenv import cli_run

from pyprojstencil.configure import PyConfig


def init_venv(config: PyConfig):
    """
    Initialize a git project

    Args:
        config: configuration for project
    """
    # run installation
    cli_run([str(config.project.joinpath(".venv")), '-p', config.pyversion])
