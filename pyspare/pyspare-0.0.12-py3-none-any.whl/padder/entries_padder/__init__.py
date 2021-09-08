from aryth.bound.entries import max_by
from texting import SP, lange, to_lpad, to_pad
from veho.entries import mapper


def entries_padder(entries, ansi=False, fill=SP):
    lpad, pad = to_lpad(ansi=ansi, fill=fill), to_pad(ansi=ansi, fill=fill)
    kw, vw = max_by(entries, lange if ansi else len)
    return mapper(entries, lambda x: lpad(x, kw), lambda tx: pad(tx, vw, tx))
