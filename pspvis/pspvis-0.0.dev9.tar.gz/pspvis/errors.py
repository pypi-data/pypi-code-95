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
pspvis's defined errors
"""


class PspVisualizeError(Exception):
    """
    Base error for pspvis(Exception):
    """


class EmptyError(PspVisualizeError):
    """
    Configuration is empty
    """
    def __init__(self):
        super().__init__('Annotation records not found, were they supplied?')


class AnnotationError(PspVisualizeError):
    """
    Base error for Annotation file errors
    """


class VisKeyError(AnnotationError, KeyError):
    """
    Key not known
    """


class MatchOverFlow(PspVisualizeError):
    """
    Too many matches
    """
    def __init__(self, *args):
        super().__init__(f'Search field: {args}')
