# This file is in the Public Domain.

import threading
import time

from .run import Bus, elapsed, getname, starttime
from .obj import Default, fmt, get, update

def __dir__():
    return("flt", "thr", "upt")

def flt(event):
    try:
        index = int(event.args[0])
        event.reply(fmt(Bus.objs[index], skip=["queue", "ready", "iqueue"]))
        return
    except (TypeError, IndexError):
        pass
    event.reply(" | ".join([getname(o) for o in Bus.objs]))


def thr(event):
    result = []
    for t in sorted(threading.enumerate(), key=lambda x: x.getName()):
        if str(t).startswith("<_"):
            continue
        o = Default()
        update(o, vars(t))
        if get(o, "sleep", None):
            up = o.sleep - int(time.time() - o.state.latest)
        else:
            up = int(time.time() - starttime)
        thrname = t.getName()
        if not thrname:
            continue
        if thrname:
            result.append((up, thrname))
    res = []
    for up, txt in sorted(result, key=lambda x: x[0]):
        res.append("%s(%s)" % (txt, elapsed(up)))
    if res:
        event.reply(" ".join(res))


def upt(event):
    event.reply("uptime is %s" % elapsed(time.time() - starttime))
