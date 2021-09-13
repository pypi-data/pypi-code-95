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
Initialize git repository
"""

import git

from pyprojstencil.configure import PyConfig


def init_git_repo(config: PyConfig):
    """
    Initialize a git project

    Args:
        config: configuration for project
    """
    proj_repo = git.Repo.init(config.project, initial_branch=config.branch)
    proj_repo.git.add(":/")
    proj_repo.index.commit('initial auto commit by pyprojstencil')
