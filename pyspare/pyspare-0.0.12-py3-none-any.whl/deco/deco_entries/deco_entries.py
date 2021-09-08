from typing import Callable, List, Tuple

from ject import oneself
from palett import fluo_entries
from palett.structs import Preset
from palett.presets import FRESH, PLANET
from texting import COLF, COSP, ELLIP, LF, liner, to_br
from texting.enum.brackets import BRK, PAR
from veho.entries import zipper
from veho.vector import mapper
from veho.vector.length import length

from pyspare.margin import EntriesMargin, entries_margin
from pyspare.padder.entries_padder import entries_padder


def deco_entries(
        entries: list,
        key_read: Callable = None,
        read: Callable = None,
        head: int = None,
        tail: int = None,
        presets: Tuple[Preset] = (FRESH, PLANET),
        effects: List[str] = None,
        delim: str = COLF,
        bracket: int = BRK,
        inner_bracket: int = PAR,
        ansi: bool = False,
        dash: str = COSP,
        rule: tuple = (ELLIP, ELLIP)
):
    size = length(entries)
    if not size: return str(entries)
    entries = entries_margin(entries, head, tail, key_read, read, rule)
    if delim.find(LF) >= 0: entries = entries_padder(entries, ansi)
    if presets: entries = fluo_entries(entries, presets, effects, colorant=False, mutate=True)
    br = to_br(inner_bracket) or oneself
    lines = mapper(entries, lambda kv: br(kv[0] + dash + kv[1].rstrip()))
    return liner(lines, delim=delim, bracket=bracket)


def deco_entries_arch(
        entries: list,
        key_read: Callable = None,
        read: Callable = None,
        head: int = None,
        tail: int = None,
        presets: Tuple[Preset] = (FRESH, PLANET),
        effects: List[str] = None,
        delim: str = COLF,
        bracket: int = BRK,
        inner_bracket: int = PAR,
        ansi: bool = False,
        dash: str = COSP
):
    size = length(entries)
    if not size: return str(entries)
    vn = EntriesMargin.build(entries, head, tail)
    raw, text = vn.to_list(ELLIP), vn.stringify(key_read, read).to_list(ELLIP)
    dye = fluo_entries(raw, presets, effects, colorant=True, mutate=True) if presets else None
    entries = entries_padder(text, raw, dye, ansi=presets or ansi) \
        if delim.find(LF) >= 0 \
        else zipper(text, dye, lambda tx, dy: dy(tx)) if presets else text
    brk = to_br(inner_bracket) or oneself
    lines = mapper(entries, lambda entry: brk(entry[0] + dash + entry[1].rstrip()))
    return liner(lines, delim=delim, bracket=bracket)
