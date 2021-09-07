# -*- coding: utf-8 -*-
#
#    TypeAtlas Morse Code Data
#    Written in 2018-2021 by Milko Krachounov
#
#    This file is part of TypeAtlas.
#
#    To the extent possible under law, Milko Krachunov has waived all copyright
#    and related or neighboring rights to TypeAtlas Morse Code Data.
#    This software is distributed without any warranty.
#
#    You should have received a copy of the CC0 legalcode along with this
#    work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
#

from collections import ChainMap
from typeatlas.charsets import add_morse_code, MULTICHAR_REMAP

N_ = lambda s: s


MORSE_INTER = {
    'A': ". -",
    'B': "- . . .",
    'C': "- . - .",
    'D': "- . .",
    'E': ".",
    'F': ". . - .",
    'G': "- - .",
    'H': ". . . .",
    'I': ". .",
    'J': ". - - -",
    'K': "- . -",
    'L': ". - . .",
    'M': "- -",
    'N': "- .",
    'O': "- - -",
    'P': ". - - .",
    'Q': "- - . -",
    'R': ". - .",
    'S': ". . .",
    'T': "-",
    'U': ". . -",
    'V': ". . . -",
    'W': ". - -",
    'X': "- . . -",
    'Y': "- . - -",
    'Z': "- - . .",
    '0': "- - - - -",
    '1': ". - - - -",
    '2': ". . - - -",
    '3': ". . . - -",
    '4': ". . . . -",
    '5': ". . . . .",
    '6': "- . . . .",
    '7': "- - . . .",
    '8': "- - - . .",
    '9': "- - - - .",
    '.': ". - . - . -",
    ',': "- - . . - -",
    '?': ". . - - . .",
    "'": ". - - - - .",
    '!': "- . - . - -",
    '/': "- . . - .",
    '(': "- . - - .",
    ')': "- . - - . -",
    '&': ". - . . .",
    ':': "- - - . . .",
    ';': "- . - . - .",
    '=': "- . . . -",
    '+': ". - . - .",
    '-': "- . . . . -",
    '_': ". . - - . -",
    '"': ". - . . - .",
    '$': ". . . - . . -",
    '@': ". - - . - .",
}



MORSE_AMERICAN = {
    'A': ". --",
    'B': "-- . . .",
    'C': ". .  .",
    'D': "-- . .",
    'E': ".",
    'F': ". -- .",
    'G': "-- -- .",
    'H': ". . . .",
    'I': ". .",
    'J': "-- . -- .",
    'K': "-- . --",
    'L': "---",
    'M': "-- --",
    'N': "-- .",
    'O': ".  .",
    'P': ". . . . .",
    'Q': ". . -- .",
    'R': ".  . .",
    'S': ". . .",
    'T': "--",
    'U': ". . --",
    'V': ". . . --",
    'W': ". -- --",
    'X': ". -- . .",
    'Y': ". .  . .",
    'Z': ". . .  .",
    '0': "-----",
    '1': ". -- -- .",
    '2': ". . -- . .",
    '3': ". . . -- .",
    '4': ". . . . --",
    '5': "-- -- --",
    '6': ". . . . . .",
    '7': "-- -- . .",
    '8': "-- . . . .",
    '9': "-- . . --",

    '.': ". . -- . .",
    ',': ". -- . --",
    '?': "-- . . -- .",
    "'": ". . -- .  . -- . .",
    '!': "-- -- -- .",
    '/': ". . --  --",
    '(': ". . . . .  -- .",
    ')': ". . . . .  . .  . .",
    '&': ".  . . .",
    ':': "-- . --  . .",
    ';': ". . .  . .",
    '“': ". . -- .  -- .",
    '”': ". . -- .  -- . -- .",
}


MORSE_INTER_PROSIGNS = {
    '🆘': ". . . - - - . . .", # SOS
    '\x04': ". . . - . -", # End of work
    '\x18': ". . . . . . . .", # Error
    '\x05': "- . -",  # Invitation to transmit
    '\x02': "- . - . - .", # Starting signal, also bell is appropriate
    '\f': ". - . - .", # New page
    '\x06': ". . . - .", # Understood
    #'': ". . . - .", # Wait
}

MORSE_INTER_NONENGLISH = {
    'À': ". - - . -",
    'Ä': ". - . -",
    'Å': ". - - . -",
    'Ą': ". - . -",
    'Æ': ". - . -",
    'Ć': "- . - . .",
    'Ĉ': "- . - . .",
    'Ç': "- . - . .",
    'CH': "- - - -",
    'Đ': ". . - . .",
    'Ð': ". . - - .",
    'É': ". . - . .",
    'È': ". - . . -",
    'Ę': ". . - . .",
    'Ĝ': "- - . - .",
    'Ĥ': "- - - -",
    'Ĵ': ". - - - .",
    'Ł': ". - . . -",
    'Ń': "- - . - -",
    'Ñ': "- - . - -",
    'Ó': "- - - .",
    'Ö': "- - - .",
    'Ø': "- - - .",
    'Ś': ". . . - . . .",
    'Ŝ': ". . . - .",
    'Š': "- - - -",
    'Þ': ". - - . .",
    'Ü': ". . - -",
    'Ŭ': ". . - -",
    'Ź': "- - . . - .",
    'Ż': "- - . . -",
}


MORSE_INTER_COMPLETE = dict(ChainMap(MORSE_INTER_NONENGLISH, MORSE_INTER))
MORSE_PERSIAN_LATIN_BASE = dict(MORSE_INTER_COMPLETE, **{
    'CH': "- - - .",
    'KH': "- . . -",
    'SH': "- - - -",
    'AI': "- - -",
    'GH': ". . - -",
})



MAP_GREEK = {
    'Α': 'A',
    'Β': 'B',
    'Γ': 'G',
    'Δ': 'D',
    'Ε': 'E',
    'Ζ': 'Z',
    'Η': 'H',
    'Θ': 'C',
    'Ι': 'I',
    'Κ': 'K',
    'Λ': 'L',
    'Μ': 'M',
    'Ν': 'N',
    'Ξ': 'X',
    'Ο': 'O',
    'Π': 'P',
    'Ρ': 'R',
    'Σ': 'S',
    'Τ': 'T',
    'Υ': 'Y',
    'Φ': 'F',
    'Χ': 'CH',
    'Ψ': 'Q',
    'Ω': 'W',
}

MAP_RUSSIAN = {
    'А': 'A',
    'Б': 'B',
    'В': 'W',
    'Г': 'G',
    'Д': 'D',
    'Е': 'E',
    'Ж': 'V',
    'З': 'Z',
    'И': 'I',
    'Й': 'J',
    'К': 'K',
    'Л': 'L',
    'М': 'M',
    'Н': 'N',
    'О': 'O',
    'П': 'P',
    'Р': 'R',
    'С': 'S',
    'Т': 'T',
    'У': 'U',
    'Ф': 'F',
    'Х': 'H',
    'Ц': 'C',
    'Ч': 'Ö',
    'Ш': 'CH',
    'Щ': 'Q',
    'Ь': 'X',
    'Ы': 'Y',
    'Э': 'É',
    'Ю': 'Ü',
    'Я': 'Ä',
    'Ї': 'Ĵ',
}

VARIANT_BULGARIAN = {
    'Ь': 'Ъ',
    'Ы': 'Ь',
}

VARIANT_UKRAINIAN = {
    'И': 'І',
    'Э': 'Є',
}

MAP_BULGARIAN = {VARIANT_BULGARIAN.get(char, char): latin
                 for char, latin in MAP_RUSSIAN.items()}

MAP_UKRAINIAN = {VARIANT_UKRAINIAN.get(char, char): latin
                 for char, latin in MAP_RUSSIAN.items()}


MAP_HEBREW = {
    'א': 'A',
    'ב': 'B',
    'ג': 'G',
    'ד': 'D',
    'ה': 'O',
    'ו': 'E',
    'ז': 'Z',
    'ח': 'H',
    'ט': 'U',
    'י': 'I',
    'כ': 'K',
    'ל': 'L',
    'מ': 'M',
    'נ': 'N',
    'ס': 'C',
    'ע': 'J',
    'פ': 'P',
    'צ': 'W',
    'ק': 'Q',
    'ר': 'R',
    'ש': 'S',

}

MAP_ARABIC = {
    'ا': 'A',
    'ب': 'B',
    'ت': 'T',
    'ث': 'C',
    'ج': 'J',
    'ح': 'H',
    'خ': 'O',
    'د': 'D',
    'ذ': 'Z',
    'ر': 'R',
    'ز': 'Ö',
    'س': 'S',
    'ش': 'CH',
    'ص': 'X',
    'ض': 'V',
    'ل': 'L',
    'م': 'M',
    'ن': 'N',
    'ه': 'É',
    'و': 'W',
    'ي': 'I',
    'ﺀ': 'E',
}

MAP_PERSIAN = {
    'ا': 'A',
    'ب': 'B',
    'پ': 'P',
    'ت': 'T',
    'ث': 'C',
    'ج': 'J',
    'چ': 'CH',
    'ح': 'H',
    'خ': 'KH',
    'د': 'D',
    'ذ': 'Z',
    'ر': 'R',
    'ز': 'J',
    'ژ': 'G',
    'س': 'S',
    'ش': 'SH',
    'ص': 'S',
    'ض': 'Z',
    'ط': 'T',
    'ظ': 'Z',
    'ع': 'AI',
    'غ': 'GH',
    'ف': 'F',
    'ق': 'Q',
    'ک': 'K',
    'گ': 'G',
    'ل': 'L',
    'م': 'M',
    'ن': 'N',
    'و': 'W',
    'ه': 'H',
    'ی': 'I',
}

MAP_KOREAN = SKATS = {
     'ㄱ': 'L',
     'ㄴ': 'F',
     'ㄷ': 'B',
     'ㄹ': 'V',
     'ㅁ': 'M',
     'ㅂ': 'W',
     'ㅅ': 'G',
     'ㅇ': 'K',
     'ㅈ': 'P',
     'ㅊ': 'C',
     'ㅋ': 'X',
     'ㅌ': 'Z',
     'ㅍ': 'O',
     'ㅎ': 'J',
     'ㅏ': 'E',
     'ㅑ': 'I',
     'ㅓ': 'T',
     'ㅕ': 'S',
     'ㅗ': 'A',
     'ㅛ': 'N',
     'ㅜ': 'H',
     'ㅠ': 'R',
     'ㅡ': 'D',
     'ㅣ': 'U',
     'ㅔ': 'TU',
     'ㅐ': 'EU',
     'ㅖ': 'SU',
     'ㅒ': 'IU',
}


FIVE_NEEDLE = {
    'A': r" /|||\ ",
    'B': r" /||\| ",
    #'C': r"",
    'D': r" |/||\ ",
    'E': r" /|\|| ",
    'F': r" |/|\| ",
    'G': r" ||/|\ ",
    'H': r" /\||| ",
    'I': r" |/\|| ",
    #'J': r"",
    'K': r" ||/\| ",
    'L': r" |||/\ ",
    'M': r" \/||| ",
    'N': r" |\/|| ",
    'O': r" ||\/| ",
    'P': r" |||\/ ",
    #'Q': r"",
    'R': r" \|/|| ",
    'S': r" |\|/| ",
    'T': r" ||\|/ ",
    #'U': r"",
    'V': r" \||/| ",
    'W': r" |\||/ ",
    #'X': r"",
    'Y': r" \|||/ ",
    #'Z': r"",
}

FIVE_NEEDLE_SUBSTITUTIONS = {
    'J': 'G',
    'Q': 'K',
    'Z': 'S',
    'U': 'V',

    'C': 'K', # ?????
    'X': 'KS', # ?????
}

FIVE_NEEDLE_FULL_ALPHABET = dict(sorted(dict(
                                    [(k, k) for k in FIVE_NEEDLE],
                                    **FIVE_NEEDLE_SUBSTITUTIONS).items()))


MORSE_GREEK = {k: MORSE_INTER_COMPLETE[v] for k, v in MAP_GREEK.items()}
MORSE_RUSSIAN = {k: MORSE_INTER_COMPLETE[v] for k, v in MAP_RUSSIAN.items()}
MORSE_BULGARIAN = {k: MORSE_INTER_COMPLETE[v] for k, v in MAP_BULGARIAN.items()}
MORSE_UKRAINIAN = {k: MORSE_INTER_COMPLETE[v] for k, v in MAP_UKRAINIAN.items()}
MORSE_HEBREW = {k: MORSE_INTER_COMPLETE[v] for k, v in MAP_HEBREW.items()}
MORSE_ARABIC = {k: MORSE_INTER_COMPLETE[v] for k, v in MAP_ARABIC.items()}
MORSE_PERSIAN = {k: MORSE_PERSIAN_LATIN_BASE[v] for k, v in MAP_PERSIAN.items()}
MORSE_KOREAN = {k: ' '.join(MORSE_INTER_COMPLETE[v] for v in vs)
                for k, vs in MAP_KOREAN.items()}
add_morse_code(N_("International Morse code (1865-present)"), MORSE_INTER)
add_morse_code(N_("International Morse code with extensions"),
               dict(ChainMap(MORSE_INTER_PROSIGNS,
                             MORSE_INTER_NONENGLISH,
                             MORSE_INTER)))
add_morse_code(N_("Morse code for Greek"), MAP_GREEK, MORSE_INTER_COMPLETE)
add_morse_code(N_("Morse code for Russian"), MAP_RUSSIAN, MORSE_INTER_COMPLETE)
add_morse_code(N_("Morse code for Bulgarian"), MAP_BULGARIAN, MORSE_INTER_COMPLETE)
add_morse_code(N_("Morse code for Ukrainian"), MAP_UKRAINIAN, MORSE_INTER_COMPLETE)
add_morse_code(N_("Morse code for Hebrew"), MAP_HEBREW, MORSE_INTER_COMPLETE)
add_morse_code(N_("Morse code for Arabic"), MAP_ARABIC, MORSE_INTER_COMPLETE)
add_morse_code(N_("Morse code for Persian"), MAP_PERSIAN, MORSE_PERSIAN_LATIN_BASE)
add_morse_code(N_("Morse code for Korean"), MAP_KOREAN, MORSE_INTER_COMPLETE,
                                            remap_mode=MULTICHAR_REMAP)
add_morse_code(N_("American Morse code (1844-1970s)"), MORSE_AMERICAN,
                                                       length_coded=True)
add_morse_code(N_("Five-needle telegraph code"), FIVE_NEEDLE_FULL_ALPHABET,
                                                 FIVE_NEEDLE,
                                                 remap_mode=MULTICHAR_REMAP,
                                                 needle_coded=True)
