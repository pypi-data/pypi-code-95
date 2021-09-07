from .select import select_values, select_entries, select_to_dict
from .Object import keys, values, entries, to_dict, DICT, SLOTS


class Object:
    @staticmethod
    def keys(ob):
        return list(ob.keys()) if isinstance(ob, dict) \
            else list(ob.__dict__.keys()) if hasattr(ob, DICT) \
            else ob.__slots__ if hasattr(ob, SLOTS) \
            else []

    @staticmethod
    def values(ob):
        return list(ob.values()) if isinstance(ob, dict) \
            else list(ob.__dict__.values()) if hasattr(ob, DICT) \
            else [getattr(ob, s) for s in ob.__slots__] if hasattr(ob, SLOTS) \
            else []

    @staticmethod
    def entries(ob):
        return list(ob.items()) if isinstance(ob, dict) \
            else list(ob.__dict__.items()) if hasattr(ob, DICT) \
            else [(s, getattr(ob, s)) for s in ob.__slots__] if hasattr(ob, SLOTS) \
            else []

    @staticmethod
    def dict(ob):
        return ob if isinstance(ob, dict) \
            else ob.__dict__ if hasattr(ob, DICT) \
            else {s: getattr(ob, s) for s in ob.__slots__} if hasattr(ob, SLOTS) \
            else {}
