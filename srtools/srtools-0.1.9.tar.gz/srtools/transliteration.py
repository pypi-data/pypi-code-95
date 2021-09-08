# -*- coding: utf-8 -*-
# srtools
# Copyright (C) 2019-2021 Andrej Radović <r.andrej@gmail.com>
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
import re

from .character_dictionaries import CYR_TO_LAT_TTABLE
from .character_dictionaries import LAT_TO_CYR_DIGRAPHS_DICT
from .character_dictionaries import LAT_TO_CYR_TTABLE

_LAT_TO_CYR_DIGRAPH_RX = (
    "(" + "|".join(map(re.escape, LAT_TO_CYR_DIGRAPHS_DICT.keys())) + ")"
)
_LAT_TO_CYR_DIGRAPH_COMP_RX = re.compile(
    _LAT_TO_CYR_DIGRAPH_RX, re.UNICODE | re.MULTILINE
)


def _cyr_sub_string_from_lat_match(match: re.Match) -> str:
    cyr_digraph = match.group()
    lat_digraph = LAT_TO_CYR_DIGRAPHS_DICT[cyr_digraph]
    return lat_digraph


def latin_to_cyrillic(text: str) -> str:
    """Transliterate Serbian Latin string to Cyrillic.

    You may use a special separator ``!`` to split digraphs `lj`, `nj`, `dž` to
    prevent their conversion to single Cyrillic letters like so: `l!j`.

    Args:
        text: input Latin string to be transliterated.

    Returns:
        str: Input string transliterated to Cyrillic.

    Examples:
        >>> from srtools import latin_to_cyrillic
        >>> in_str = "Đače, uštedu plaćaj žaljenjem zbog džinovskih cifara."
        >>> latin_to_cyrillic(in_str)
        'Ђаче, уштеду плаћај жаљењем због џиновских цифара.'
        >>> latin_to_cyrillic('N!J je skraćenica za Nju Džersi')
        'НЈ је скраћеница за Њу Џерси'
    """
    text_digraphs_substituted = _LAT_TO_CYR_DIGRAPH_COMP_RX.sub(
        _cyr_sub_string_from_lat_match, text
    )
    text_digraphs_and_letters_substituted = (
        text_digraphs_substituted.translate(LAT_TO_CYR_TTABLE)
    )
    return text_digraphs_and_letters_substituted


def cyrillic_to_latin(text: str) -> str:
    """Transliterate Serbian Cyrillic string to Latin.

    Args:
        text: input Cyrillic string to be transliterated.

    Returns:
        str: Input string transliterated to Latin.

    Examples:
        >>> from srtools import cyrillic_to_latin
        >>> in_str = "Ђаче, уштеду плаћај жаљењем због џиновских цифара."
        >>> cyrillic_to_latin(in_str)
        'Đače, uštedu plaćaj žaljenjem zbog džinovskih cifara.'
    """
    return text.translate(CYR_TO_LAT_TTABLE)
