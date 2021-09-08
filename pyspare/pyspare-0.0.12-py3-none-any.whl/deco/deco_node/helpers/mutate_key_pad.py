from texting import lange


def mutate_key_pad(entries):
    wd, hi = 0, len(entries)
    while (hi := hi - 1) >= 0:
        k, v = entries[hi]
        wd = max(lange(k := str(k)), wd)
        entries[hi] = k, v
    return wd
