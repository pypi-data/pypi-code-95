from texting import tags


def wl(m):
    print(m)


def wr_tags(*labels, **items):
    msg = tags(*labels, **items)
    wl(msg)
    return msg
