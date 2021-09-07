"""pccs.__init__

PCCS (Practical Color Coordinate System) for Python core library
================================================================

References
----------

The algolythm of the conversion between PCCS and Munsell color system
is based on the paper bellow:

-   Kobayashi, Mituo; and Yosiki, Kayoko. 2001. Mathematical Relation
    among PCCS Tones, PCCS Color Attributes and Munsell Color
    Attributes. Nihon Shikisai Gakkai Shi [Color Science Association of
    Japan] 25 (4), 249-261.
"""


import re
from math import e, pi, sin, cos, sqrt
from collections.abc import Sequence

from colour.constants import FLOATING_POINT_NUMBER_PATTERN
from colour.notation.munsell import (munsell_specification_to_munsell_colour,
                                     munsell_colour_to_munsell_specification, normalize_munsell_specification)
from sympy import Symbol, solve


__all__ = [
    'PCCS_HUE_CODES', 'PCCS_TONE_COORDS', 'PCCS_TONE_NAMES',
    'PCCS_HUE_NAME_PATTERN', 'PCCS_GREY_LONG_PATTERN',
    'PCCS_COLOUR_LONG_PATTERN', 'PCCS_GREY_PATTERN', 'PCCS_COLOUR_PATTERN',
    'munsell_linear_hue_scale_to_hue_step_and_code',
    'munsell_hue_step_and_code_to_linear_hue_scale',
    'pccs_specification_to_munsell_specification',
    'munsell_specification_to_pccs_specification',
    'tilde_C', 'tilde_lambda',
    'pccs_tone_to_lightness_and_saturation',
    'pccs_lightness_and_saturation_to_tone',
    'parse_pccs_colour', 'pccs_hue_code_to_float', 'round_align',
    'pccs_colour_to_pccs_specification', 'pccs_specification_to_pccs_colour'
]


PCCS_HUE_CODES = [
    '1:pR',
    '2:R',
    '3:yR',
    '4:rO',
    '5:O',
    '6:yO',
    '7:rY',
    '8:Y',
    '9:gY',
    '10:YG',
    '11:yG',
    '12:G',
    '13:bG',
    '14:BG',
    '15:BG',
    '16:gB',
    '17:B',
    '18:B',
    '19:pB',
    '20:V',
    '21:bP',
    '22:P',
    '23:rP',
    '24:RP',
]
PCCS_TONE_COORDS = {
    # r:    (s, t)
    'p':    (2, 8.6),
    'p+':   (3, 8.2),
    'ltg':  (2, 7.1),
    'g':    (2, 4.1),
    'dkg':  (2, 2.1),
    'lt':   (5, 7.8),
    'lt+':  (6, 7.3),
    'sf':   (5, 6.3),
    'd':    (5, 4.8),
    'dk':   (5, 3.0),
    'b':    (8, 6.6),
    's':    (8, 5.2),
    'dp':   (8, 4.1),
    'v':    (9, 5.5),
}
PCCS_TONE_NAMES = list(PCCS_TONE_COORDS.keys())

PCCS_HUE_NAME_PATTERN = '|'.join(PCCS_HUE_CODES)
PCCS_GREY_LONG_PATTERN = ('n-(?P<value>{0})'
                          .format(FLOATING_POINT_NUMBER_PATTERN))
PCCS_COLOUR_LONG_PATTERN = ('(?P<hue_name>{0})'
                            '-(?P<lightness>{1})'
                            '-(?P<saturation>{1})s'
                            .format(PCCS_HUE_NAME_PATTERN,
                                    FLOATING_POINT_NUMBER_PATTERN))
PCCS_GREY_PATTERN = 'Gy-(?P<value>{0})'.format(FLOATING_POINT_NUMBER_PATTERN)
PCCS_COLOUR_PATTERN = ('(?P<tone>ltg|dkg|lt\\+?|dk|dp|sf|p\\+?|d|g|b|s|v)'
                       '(?P<hue>{0})'
                       .format(FLOATING_POINT_NUMBER_PATTERN))


def munsell_linear_hue_scale_to_hue_step_and_code(H: float) -> tuple[float, float]:
    """(internal) Convert Munsell linear hue scale to step and code hue
    notation

    Convert 0-100 linear hue scale to 1-10 hue step and base letter
    code of Munsell color system in format of the intermediate
    specification used in the colour.notaion.musell library of the
    coulour-science package.


    Notes
    -----

    The linear hue scale which takes 0 to 100 is used in the
    specification of PCCS and the reference article. They use 0 (== 100)
    for 10RP, 10 for 10R, 20 for 10YR, etc.

    On the other hand, 10 steps of values and letter codes are the way
    to describe hue in the Munsell color system itself, but the order
    (indices) for the codes used in the intermediate specification of
    colour.notation.musell library are different from that in linear
    scale above. The indices of the hue codes are:

        1: B
        2: BG
        3: G
        4: GY
        5: Y
        6: YR
        7: R
        8: RP
        9: P
        10: PB

    Notice not only that they start counting with different hue codes
    but also they conunts the codes in different directions! PCCS specs
    count them clockwise, while The munsell library do counterclockwise.

    The function covers only the conversion of that above.

    >>> munsell_linear_hue_scale_to_hue_step_and_code(0.0)
    (10.0, 8.0)
    >>> munsell_linear_hue_scale_to_hue_step_and_code(4.0)
    (4.0, 7.0)
    >>> munsell_linear_hue_scale_to_hue_step_and_code(22.0)
    (2.0, 5.0)
    >>> munsell_linear_hue_scale_to_hue_step_and_code(43.0)
    (3.0, 3.0)
    >>> munsell_linear_hue_scale_to_hue_step_and_code(60.0)
    (10.0, 2.0)
    >>> munsell_linear_hue_scale_to_hue_step_and_code(83.0)
    (3.0, 9.0)
    """

    H1, H2 = divmod(H, 10.0)
    step = H2 % 10.0
    if step == 0.0:
        step = 10.0
        H1 -= 1.0
    code = (10.0 - H1 + 6.0) % 10.0 + 1.0
    return step, code


def munsell_hue_step_and_code_to_linear_hue_scale(
        step: float, code: float) -> float:
    """(internal) Convert Munsell step and code hue notation to linear
    hue scale

    This is the opposite version of
    munsell_linear_hue_scale_to_hue_step_and_code function.
    Read the notes for the function for the detail.

    >>> munsell_hue_step_and_code_to_linear_hue_scale(10.0, 8.0)
    0.0
    >>> munsell_hue_step_and_code_to_linear_hue_scale(4.0, 6.0)
    14.0
    >>> munsell_hue_step_and_code_to_linear_hue_scale(3.0, 4.0)
    33.0
    >>> munsell_hue_step_and_code_to_linear_hue_scale(10.0, 2.0)
    60.0
    >>> munsell_hue_step_and_code_to_linear_hue_scale(10.0, 1.0)
    70.0
    >>> munsell_hue_step_and_code_to_linear_hue_scale(3.0, 10.0)
    73.0
    >>> munsell_hue_step_and_code_to_linear_hue_scale(6.0, 8.0)
    96.0
    """

    H1 = (10.0 - (code - 1.0) + 6.0) % 10.0
    H2 = step
    H = (H1 * 10.0 + H2) % 100.0
    return H


def pccs_specification_to_munsell_specification(
        h: float, l: float, s: float
            ) -> tuple[float, float, float, float]:
    """Convert PCCS intermediate specification values to Munsell color
    system intermediate specification values.

    PCCS specification is a sequence of three float values:

    h (float) [1-24]:       Hue. '1:pR' to '24:RP'.
    l (float) [1.5-9.5]:    Lightness. It is identical to Value in the
                            Munsell system.
    s (float) [0-10]:       Saturation.

    Munsell specification (on the munsell library) is a sequence of
    four float values:

    step (float) [1-10]:    Sub-step hue value for the letter code.
                            The value is named `hue` in the original
                            library code.
    V (float) [0-10]:       Value. It si identical to Lightness in the
                            PCCS.
    C (float) [0-14]:       Chroma. Represents purity of a color.
    code (float) [1-10]:    Hue letter code. 1 for 'B', 2 for 'BG', 3
                            for 'G', etc.

    >>> pccs_specification_to_munsell_specification(12.0, 5.5, 9.0)
    (3.0, 5.5, 12.0, 3.0)
    >>> pccs_specification_to_munsell_specification(2.0, 8.5, 2.0)
    (3.5, 8.5, 2.0, 7.0)
    """

    V = l

    x = (h - 1) / 12 * pi
    H = (100 / (2 * pi) * x - 1.0
         + 0.12 * cos(x) + 0.34 * cos(2 * x) + 0.40 * cos(3 * x)
         - 2.7 * sin(x) + 1.5 * sin(2 * x) - 0.40 * sin(3 * x))

    C = (tilde_C(h)
         * (0.077 * s + 0.0040 * s ** 2)
         * (1 - e ** (-tilde_lambda(h) * l)))

    step, code = munsell_linear_hue_scale_to_hue_step_and_code(H)
    step = round_align(step, 0.5)
    V = round_align(V, 0.5)
    C = round_align(C, 0.5)
    return step, V, C, code


def munsell_specification_to_pccs_specification(
        step: float, V: float, C: float, code: float
            ) -> tuple[float, float, float]:
    """Convert Munsell color system intermediate specification values
    to PCCS intermediate specification values.

    This is the opposite version of
    pccs_specification_to_munsell_specification function.

    >>> munsell_specification_to_pccs_specification(3.0, 5.5, 12.0, 3.0)
    (12.0, 5.5, 9.0)
    >>> munsell_specification_to_pccs_specification(3.5, 8.5, 2.0, 7.0)
    (2.0, 8.5, 2.0)
    """

    # Note: `np.nan` returns `False` when it is compared to itself.
    step = step if step == step else 0.0
    V = V if V == V else 0.0
    C = C if C == C else 0.0
    code = code if code == code else 0.0

    l = V

    if step == C == code == 0.0:
        h = 0.0
        s = 0.0
    else:
        H = munsell_hue_step_and_code_to_linear_hue_scale(step, code)
        y = H / 50 * pi
        h = ((24 / (2 * pi)) * y + 1.24
            + 0.020 * cos(y) - 0.10 * cos(2 * y) - 0.11 * cos (3 * y)
            + 0.68 * sin(y) - 0.30 * sin(2 * y) + 0.013 * sin(3 * y))

        s_ = Symbol('s')
        solutions = solve(0.0040 * s_ ** 2
                        + 0.077 * s_
                        - C / (tilde_C(h) * (1 - e ** (-tilde_lambda(h) * V))))
        s = float(max(solutions))

    h = round_align(h, 0.5)
    l = round_align(l, 0.5)
    s = round_align(s, 0.5)

    return h, l, s



def tilde_C(h: float) -> float:
    """(internal) The formula (4) on the reference paper. """

    return 12 + 1.7 * sin((h + 2.2 / 12 * pi))


def tilde_lambda(h: float) -> float:
    """(internal) The formula (2) on the reference paper. """

    return 0.81 - 0.24 * sin((h - 2.6) / 12 * pi)


def pccs_tone_to_lightness_and_saturation(
        h: float, r: str) -> tuple[float, float]:
    """Return lightness and saturation value of tone on the given hue value

    >>> pccs_tone_to_lightness_and_saturation(2.0, 'p')
    (8.5, 2.0)
    >>> pccs_tone_to_lightness_and_saturation(2.0, 'ltg')
    (7.0, 2.0)
    >>> pccs_tone_to_lightness_and_saturation(22.0, 'dp')
    (2.5, 8.0)
    """

    s, t = PCCS_TONE_COORDS[r]
    l = t + (0.25 - 0.34 * sqrt(1 - sin((h - 2) / 12 * pi))) * s

    s = round_align(s, 0.5)
    l = round_align(l, 0.5)

    return l, s


def pccs_lightness_and_saturation_to_tone(h: float, l: float, s: float) -> str:
    """Return PCCS tone name from lightness and saturation value on the
    given hue value

    >>> pccs_lightness_and_saturation_to_tone(12.0, 5.5, 9.0)
    'v'
    >>> pccs_lightness_and_saturation_to_tone(2.0, 8.5, 2.0)
    'p'
    """

    t = l - (0.25 - 0.34 * sqrt(1 - sin((h - 2) / 12 * pi))) * s
    distances = [((s0 - s) ** 2 + (t0 - t)) ** 2
                 for s0, t0
                 in PCCS_TONE_COORDS.values()]
    i = distances.index(min(distances))
    return PCCS_TONE_NAMES[i]


def parse_pccs_colour(pccs_colour: str) -> tuple[float, float, float]:
    """Convert PCCS expression to intermediate specification values

    >>> parse_pccs_colour('v12')
    (12.0, 5.5, 9.0)
    >>> parse_pccs_colour('p2')
    (2.0, 8.5, 2.0)
    >>> parse_pccs_colour('Gy-5.5')
    (0.0, 5.5, 0.0)
    >>> parse_pccs_colour('W')
    (0.0, 9.5, 0.0)
    >>> parse_pccs_colour('Bk')
    (0.0, 1.5, 0.0)
    >>> parse_pccs_colour('12:G-5.5-9s')
    (12.0, 5.5, 9.0)
    >>> parse_pccs_colour('2:R-8.5-2s')
    (2.0, 8.5, 2.0)
    >>> parse_pccs_colour('n-5.5')
    (0.0, 5.5, 0.0)
    >>> parse_pccs_colour('n-9.5')
    (0.0, 9.5, 0.0)
    >>> parse_pccs_colour('n-1.5')
    (0.0, 1.5, 0.0)
    """

    if pccs_colour == 'W':
        return 0.0, 9.5, 0.0

    if pccs_colour == 'Bk':
        return 0.0, 1.5, 0.0

    match = re.match(PCCS_GREY_PATTERN, pccs_colour, flags=re.I)
    if match:
        h = 0.0
        l = float(match.group('value'))
        s = 0.0
        return h, l, s

    match = re.match(PCCS_COLOUR_PATTERN, pccs_colour, flags=re.I)
    if match:
        h = float(match.group('hue'))
        r = match.group('tone')
        l, s = pccs_tone_to_lightness_and_saturation(h, r)
        return h, l, s

    match = re.match(PCCS_GREY_LONG_PATTERN, pccs_colour, flags=re.I)
    if match:
        h = 0.0
        l = float(match.group('value'))
        s = 0.0
        return h, l, s

    match = re.match(PCCS_COLOUR_LONG_PATTERN, pccs_colour, flags=re.I)
    if match:
        h = pccs_hue_code_to_float(match.group('hue_name'))
        l = float(match.group('lightness'))
        s = float(match.group('saturation'))
        return h, l, s

    raise ValueError('invalid PCCS expression')


def pccs_hue_code_to_float(hue_name: str) -> float:
    """Return float hue value from PCCS hue code (e.g. '1:pR')

    >>> pccs_hue_code_to_float('2:R')
    2.0
    >>> pccs_hue_code_to_float('4:rO')
    4.0
    """

    return float(PCCS_HUE_CODES.index(hue_name) + 1)


def round_align(value: float, scale: float) -> float:
    """(internal) Round value to given alignment scale.

    >>> round_align(1.0, 0.5)
    1.0
    >>> round_align(1.4, 0.5)
    1.5
    >>> round_align(1.6, 0.5)
    1.5
    >>> round_align(1.8, 0.5)
    2.0
    """

    return round(value / scale) * scale


def pccs_colour_to_pccs_specification(
        pccs_colour: str) -> tuple[float, float, float]:
    """Convert from PCCS color to PCCS intermediate specificaion
    """
    return parse_pccs_colour(pccs_colour)


def pccs_specification_to_pccs_colour(
        specification: Sequence[float, float, float],
        long: bool = False) -> str:
    """Convert from PCCS intermediate specification to PCCS color

    >>> pccs_specification_to_pccs_colour((12.0,  5.5, 9.0))
    'v12'
    >>> pccs_specification_to_pccs_colour((2.0,  8.5, 2.0))
    'p2'
    >>> pccs_specification_to_pccs_colour((0.0,  5.5, 0.0))
    'Gy-5.5'
    >>> pccs_specification_to_pccs_colour((0.0,  9.5, 0.0))
    'W'
    >>> pccs_specification_to_pccs_colour((0.0,  1.5, 0.0))
    'Bk'
    >>> pccs_specification_to_pccs_colour((12.0,  5.5, 9.0), long=True)
    '12:G-5.5-9s'
    >>> pccs_specification_to_pccs_colour((2.0,  8.5, 2.0), long=True)
    '2:R-8.5-2s'
    >>> pccs_specification_to_pccs_colour((0.0,  5.5, 0.0), long=True)
    'n-5.5'
    >>> pccs_specification_to_pccs_colour((0.0,  9.5, 0.0), long=True)
    'n-9.5'
    >>> pccs_specification_to_pccs_colour((0.0,  1.5, 0.0), long=True)
    'n-1.5'
    """

    h, l, s = specification

    if long:
        if h == s == 0.0:
            return 'n-{0}'.format(l)
        hue_name = PCCS_HUE_CODES[round(h)-1]
        if s % 1 == 0:
            s = int(s)
        return '{0}-{1}-{2}s'.format(hue_name, l, s)
    else:
        if h == s == 0.0:
            if l >= 9.5:
                return 'W'
            if l <= 1.5:
                return 'Bk'
            return 'Gy-{0}'.format(l)
        t = pccs_lightness_and_saturation_to_tone(h, l, s)
        if h % 1 == 0:
            h = int(h)
        return '{0}{1}'.format(t, h)


def pccs_colour_to_munsell_colour(pccs_colour: str) -> str:
    """Convert given PCCS color to Munsell color

    >>> pccs_colour_to_munsell_colour('v1')
    '10.0RP 4.5/13.5'
    >>> pccs_colour_to_munsell_colour('v2')
    '3.5R 4.5/13.0'
    >>> pccs_colour_to_munsell_colour('b22')
    '7.0P 5.0/9.5'
    >>> pccs_colour_to_munsell_colour('dk18')
    '3.0PB 2.0/5.0'
    >>> pccs_colour_to_munsell_colour('W')
    'N9.5'
    >>> pccs_colour_to_munsell_colour('Bk')
    'N1.5'
    """

    h, l, s = pccs_colour_to_pccs_specification(pccs_colour)
    H2, V, C, H1 = pccs_specification_to_munsell_specification(h, l, s)
    H2, V, C, H1 = normalize_munsell_specification((H2, V, C, H1))
    return munsell_specification_to_munsell_colour((H2, V, C, H1))


def munsell_colour_to_pccs_colour(munsell_colour: str) -> str:
    """Convert given Munsell color to PCCS color

    >>> munsell_colour_to_pccs_colour('10.0RP 4.5/13.5')
    'v1'
    >>> munsell_colour_to_pccs_colour('3.5R 4.5/13.0')
    'v2'
    >>> munsell_colour_to_pccs_colour('7.0P 5.0/9.5')
    'b22'
    >>> munsell_colour_to_pccs_colour('3.0PB 2.0/5.0')
    'dk18'
    >>> munsell_colour_to_pccs_colour('N9.5')
    'W'
    >>> munsell_colour_to_pccs_colour('N1.5')
    'Bk'
    """

    munsell_spec = munsell_colour_to_munsell_specification(munsell_colour)
    step, V, C, code = munsell_spec
    h, l, s = munsell_specification_to_pccs_specification(step, V, C, code)
    return pccs_specification_to_pccs_colour((h, l, s))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
