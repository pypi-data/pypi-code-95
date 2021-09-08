import re
from functools import partial

from palett.fluo import fluo_vector
from palett.presets import ATLAS, SUBTLE
from texting import LF, TB, fold, has_ansi, ripper, VO
from texting.enum.regexes import LITERAL

splitter = partial(ripper, re.compile(LITERAL))


def deco_str(
        text,
        width=80,
        indent=0,
        first_line_indent=0,
        presets=(ATLAS, SUBTLE),
        effects=None,
        vectify=splitter,
        joiner=None
):
    if not (size := len(text)): return ''
    if has_ansi(text): return text
    if width and size > width: text = fold(
        text,
        width=width,
        delim=LF + TB * (indent if indent else 0),
        first_line_indent=first_line_indent
    )
    if presets: text = fluo_string(text, presets, effects, vectify, joiner)
    return text


def fluo_string(text, presets, effects, vectify, joiner):
    words = vectify(text)
    fluo_vector(words, presets, effects, mutate=True)
    return joiner(words) if joiner else VO.join(words)
