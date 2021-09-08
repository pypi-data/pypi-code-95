from typing import Callable, List, Tuple

from palett.structs import Preset
from palett.presets import FRESH, PLANET
from texting import COLF, RTSP
from texting.enum.brackets import BRC

from pyspare.deco.deco_entries.deco_dict import deco_dict


def deco_object(
        ob,
        key_read: Callable = None,
        read: Callable = None,
        presets: Tuple[Preset] = (FRESH, PLANET),
        effects: List[str] = None,
        delim: str = COLF,
        bracket: int = BRC,
        ansi: bool = False,
        dash: str = RTSP,
        total: bool = False
):
    lex = {}
    if hasattr(ob, '__slots__') and ob.__slots__:
        lex.update({s: getattr(ob, s) for s in ob.__slots__})
    if hasattr(ob, '__dict__') and ob.__dict__:
        lex.update(ob.__dict__)
    if hasattr(ob, '_fields') and ob._fields:
        lex.update({s: getattr(ob, s) for s in ob._fields})
    if total: lex = {s: getattr(ob, s) for s in dir(ob)}
    type_name = ob.__doc__ if hasattr(ob, '__doc__') else type(ob).__name__
    content = deco_dict(lex,
                        key_read=key_read,
                        read=read,
                        presets=presets,
                        effects=effects,
                        delim=delim,
                        bracket=bracket,
                        ansi=ansi,
                        dash=dash) if lex else str(ob)
    return f'[{type_name}] {content}'
