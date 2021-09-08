from typing import Callable, List, Tuple

from palett.presets import FRESH, PLANET
from palett.structs import Preset
from texting import COLF, ELLIP, RTSP
from texting.enum.brackets import BRC, NONE

from pyspare.deco.deco_entries.deco_entries import deco_entries


def deco_dict(
        lex: dict,
        key_read: Callable = None,
        read: Callable = None,
        head: int = None,
        tail: int = None,
        presets: Tuple[Preset] = (FRESH, PLANET),
        effects: List[str] = None,
        delim: str = COLF,
        bracket: int = BRC,
        ansi: bool = False,
        dash: str = RTSP,
        rule: tuple = (ELLIP, ELLIP)
):
    if not isinstance(lex, dict) or not len(lex): return str(lex)
    return deco_entries(list(lex.items()),
                        key_read=key_read,
                        read=read,
                        head=head,
                        tail=tail,
                        presets=presets,
                        effects=effects,
                        delim=delim,
                        bracket=bracket,
                        inner_bracket=NONE,
                        ansi=ansi,
                        dash=dash,
                        rule=rule)
