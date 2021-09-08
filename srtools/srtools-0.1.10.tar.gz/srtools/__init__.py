# -*- coding: utf-8 -*-
# srtools
# Copyright (C) 2019-2021  Andrej Radović <r.andrej@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from ._version import __version__
from .character_dictionaries import CYR_TO_LAT_DICT
from .character_dictionaries import CYR_TO_LAT_TTABLE
from .character_dictionaries import LAT_TO_CYR_DICT
from .character_dictionaries import LAT_TO_CYR_DIGRAPHS_DICT
from .character_dictionaries import LAT_TO_CYR_TTABLE
from .transliteration import cyrillic_to_latin
from .transliteration import latin_to_cyrillic


__all__ = (
    "CYR_TO_LAT_DICT",
    "CYR_TO_LAT_TTABLE",
    "LAT_TO_CYR_DICT",
    "LAT_TO_CYR_DIGRAPHS_DICT",
    "LAT_TO_CYR_TTABLE",
    "__version__",
    "cyrillic_to_latin",
    "latin_to_cyrillic",
)
