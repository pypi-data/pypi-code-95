from aryth.bound.vector import max_by
from texting import SP, lange, to_pad
from veho.vector import duozipper, trizipper


def vector_padder(text, raw=None, dye=None, ansi=False, fill=SP):
    raw = raw if raw is not None else text
    pad = to_pad(ansi=ansi, fill=fill)
    wd = max_by(text, lange if ansi else len)
    return trizipper(text, raw, dye, lambda tx, va, dy: dy(pad(tx, wd, va))) \
        if dye \
        else duozipper(text, raw, lambda tx, va: pad(tx, wd, va))
