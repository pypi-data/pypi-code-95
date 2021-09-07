DICT = '__dict__'
SLOTS = '__slots__'


# def select_values(obj, *keys):
#     return [getattr(obj, k, None) for k in keys]


def select_values(ob, *keys):
    if hasattr(ob, DICT) or hasattr(ob, SLOTS): return [getattr(ob, k, None) for k in keys]
    if isinstance(ob, dict): return [ob[k] if k in ob else None for k in keys]
    if isinstance(ob, list) and (hi := len(ob)) and (lo := -hi):
        return [ob[k] if isinstance(k, int) and lo <= k < hi else None for k in keys]
    return []


def select_entries(ob, keys):
    if hasattr(ob, DICT) or hasattr(ob, SLOTS): return [(k, getattr(ob, k, None)) for k in keys]
    if isinstance(ob, dict): return [(k, ob[k]) if k in ob else None for k in keys]
    if isinstance(ob, list) and (hi := len(ob)) and (lo := -hi):
        return [(k, ob[k]) if isinstance(k, int) and lo <= k < hi else None for k in keys]
    return []


def select_to_dict(ob, *keys):
    if hasattr(ob, DICT) or hasattr(ob, SLOTS): return {k: getattr(ob, k, None) for k in keys}
    if isinstance(ob, dict): return {k: ob[k] if k in ob else None for k in keys}
    if isinstance(ob, list) and (hi := len(ob)) and (lo := -hi):
        return {k: ob[k] if isinstance(k, int) and lo <= k < hi else None for k in keys}
    return {}
