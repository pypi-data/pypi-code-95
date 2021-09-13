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
Thrown errors
"""

import os


class PyProjStencilError(Exception):
    """
    Base Exception for project-thrown errors
    """


class NoProjectNameError(PyProjStencilError):
    """
    Project-Name not provided
    """
    def __init__(self):
        super(PyProjStencilError, self).__init__('''
        Project Name was not provided.
        ''')


class LicenseNotKnownError(PyProjStencilError):
    """
    This license is not known
    """
    def __init__(self, l_name: str):
        super(PyProjStencilError, self).__init__(f'''
        Supplied license {l_name} is not known,
        considering using "custom" for --license
        and adding the license/headers by hand
        ''')


class TemplateMissingError(PyProjStencilError):
    """
    Template folder missing
    """
    def __init__(self, root: os.PathLike):
        super(PyProjStencilError, self).__init__(f'''
        Template directory path {root} not found
        ''')


class MaxRecursion(PyProjStencilError):
    """
    File Structure too deep
    """
    def __init__(self, source: os.PathLike):
        super(PyProjStencilError, self).__init__(f'''
        reached maximum number of recursions, error at path {source}
        ''')
