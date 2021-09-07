DICT = '__dict__'
SLOTS = '__slots__'


def keys(ob):
    return list(ob.__dict__.keys()) if hasattr(ob, DICT) \
        else ob.__slots__ if hasattr(ob, SLOTS) \
        else list(ob.keys()) if isinstance(ob, dict) \
        else [i for i, _ in enumerate(ob)] if isinstance(ob, list) \
        else []


def values(ob):
    return list(ob.__dict__.values()) if hasattr(ob, DICT) \
        else [getattr(ob, s) for s in ob.__slots__] if hasattr(ob, SLOTS) \
        else list(ob.values()) if isinstance(ob, dict) \
        else ob[:] if isinstance(ob, list) \
        else []


def entries(ob):
    return [(s, getattr(ob, s)) for s in ob.__slots__] if hasattr(ob, SLOTS) \
        else list(ob.__dict__.items()) if hasattr(ob, DICT) \
        else list(ob.items()) if isinstance(ob, dict) \
        else list(enumerate(ob)) if isinstance(ob, list) \
        else []


def to_dict(ob):
    return ob.__dict__ if hasattr(ob, DICT) \
        else {s: getattr(ob, s) for s in ob.__slots__} if hasattr(ob, SLOTS) \
        else ob if isinstance(ob, dict) \
        else dict(enumerate(ob)) if isinstance(ob, list) \
        else {}
