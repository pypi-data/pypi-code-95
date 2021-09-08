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
from typing import Dict
from typing import Set
from typing import Tuple
from unicodedata import normalize

_CYR_LAT_LOWERCASE_LETTER_PAIRS: Set[Tuple[str, str]] = {
    ("а", "a"),
    ("б", "b"),
    ("в", "v"),
    ("г", "g"),
    ("д", "d"),
    ("ђ", "đ"),
    ("е", "e"),
    ("ж", "ž"),
    ("з", "z"),
    ("и", "i"),
    ("ј", "j"),
    ("к", "k"),
    ("л", "l"),
    ("љ", "lj"),
    ("м", "m"),
    ("н", "n"),
    ("њ", "nj"),
    ("о", "o"),
    ("п", "p"),
    ("р", "r"),
    ("с", "s"),
    ("т", "t"),
    ("ћ", "ć"),
    ("у", "u"),
    ("ф", "f"),
    ("х", "h"),
    ("ц", "c"),
    ("ч", "č"),
    ("џ", "dž"),
    ("ш", "š"),
}

_SERBIAN_ACCENTS: Set[str] = {
    "\N{COMBINING DOUBLE GRAVE ACCENT}",
    "\N{COMBINING GRAVE ACCENT}",
    "\N{COMBINING INVERTED BREVE}",
    "\N{COMBINING ACUTE ACCENT}",
    "\N{COMBINING MACRON}",
    "\N{COMBINING OVERLINE}",
    "\N{COMBINING CIRCUMFLEX ACCENT}",
    "\N{COMBINING BREVE}",
}
_VOWEL_PAIRS: Set[Tuple[str, str]] = {
    ("а", "a"),
    ("е", "e"),
    ("и", "i"),
    ("о", "o"),
    ("у", "u"),
}
_ACCENTED_VOWEL_PAIRS = {
    (normalize("NFC", cyr_ltr + acc), normalize("NFC", lat_ltr + acc))
    for acc in _SERBIAN_ACCENTS
    for cyr_ltr, lat_ltr in _VOWEL_PAIRS
}
_CYR_LAT_LOWERCASE_LETTER_PAIRS.union(_ACCENTED_VOWEL_PAIRS)


def _cat_dicts(*args: dict) -> Dict[any, any]:
    result = {}
    for dct in args:
        result.update(dct)
    return result


def _generate_cyr_to_lat_dictionary() -> Dict[str, str]:
    lowercase_dict = {
        cyr_letter: lat_letter
        for cyr_letter, lat_letter in _CYR_LAT_LOWERCASE_LETTER_PAIRS
    }
    uppercase_dict = {
        cyr_letter.upper(): lat_letter.capitalize()
        for cyr_letter, lat_letter in _CYR_LAT_LOWERCASE_LETTER_PAIRS
    }
    return _cat_dicts(lowercase_dict, uppercase_dict)


CYR_TO_LAT_DICT: Dict[str, str] = _generate_cyr_to_lat_dictionary()
"""Dict[str, str]: Cyrillic → Latin character translation dict.

Not used internally. Can be used to look up equivalent Latin letter strings.
"""

CYR_TO_LAT_TTABLE: Dict[int, str] = str.maketrans(CYR_TO_LAT_DICT)
"""Dict[int, str]: Cyrillic → Latin character translation table.

Used internally with :meth:`str.translate()` to transliterate text.
"""

DIGRAPH_ESCAPE_CHARACTER = "!"


def _generate_lat_to_cyr_dictionary() -> Dict[str, str]:
    lowercase_dict = {
        lat_letter: cyr_letter
        for cyr_letter, lat_letter in _CYR_LAT_LOWERCASE_LETTER_PAIRS
    }

    lowercase_letters = {
        lat_letter: cyr_letter
        for lat_letter, cyr_letter in lowercase_dict.items()
        if len(lat_letter) == 1
    }
    uppercase_letters = {
        lat_letter.upper(): cyr_letter.upper()
        for lat_letter, cyr_letter in lowercase_letters.items()
    }

    all_letters_dict = _cat_dicts(lowercase_letters, uppercase_letters)
    all_letters_ttable = str.maketrans(all_letters_dict)

    lowercase_digraphs = {
        lat_letter: cyr_letter
        for lat_letter, cyr_letter in lowercase_dict.items()
        if len(lat_letter) == 2
    }
    lowercase_escaped_digraphs = {
        (
            lat_letter[0] + DIGRAPH_ESCAPE_CHARACTER + lat_letter[1]
        ): lat_letter.translate(all_letters_ttable)
        for lat_letter in lowercase_digraphs.keys()
    }

    lowercase_all_digraphs = _cat_dicts(
        lowercase_digraphs, lowercase_escaped_digraphs
    )

    uppercase_digraphs = {
        lat_letter.upper(): cyr_letter.upper()
        for lat_letter, cyr_letter in lowercase_all_digraphs.items()
    }
    capitalized_digraphs = {
        lat_letter.capitalize(): cyr_letter.capitalize()
        for lat_letter, cyr_letter in lowercase_all_digraphs.items()
    }

    all_digraphs = _cat_dicts(
        lowercase_all_digraphs, capitalized_digraphs, uppercase_digraphs
    )

    return (
        all_letters_ttable,
        all_digraphs,
        _cat_dicts(
            lowercase_letters,
            uppercase_letters,
            lowercase_digraphs,
            lowercase_escaped_digraphs,
            uppercase_digraphs,
            capitalized_digraphs,
        ),
    )


LAT_TO_CYR_TTABLE: Dict[int, str]
"""Dict[int, str]: Latin → Cyrillic character translation table.

Covers only transitions from single-character Latin letters to equivalent
Cyrillic letters.
Used internally with :meth:`str.translate()` to transliterate text.
"""

LAT_TO_CYR_DIGRAPHS_DICT: Dict[str, str]
"""Dict[str, str]: Latin → Cyrillic digraph translation dict.

Covers only mappings from Latin digraphs to equivalent Cyrillic letters.
Used internally with :meth:`str.translate()` to transliterate text.
"""

LAT_TO_CYR_DICT: Dict[str, str]
"""Dict[str, str]: Latin → Cyrillic character translation dict.

Not used internally. Can be used to look up equivalent Cyrillic letter strings.
"""

(
    LAT_TO_CYR_TTABLE,
    LAT_TO_CYR_DIGRAPHS_DICT,
    LAT_TO_CYR_DICT,
) = _generate_lat_to_cyr_dictionary()
