from .missing import MISSING
from .field import Field


class TypeField(Field):
    def __init__(self, field_type: type = None, /, *, default=MISSING, default_factory=MISSING, optional: bool = False):
        super().__init__(default, default_factory, optional)
        self.type = field_type

    def __repr__(self):
        attrs = [f"type={self.type.__name__}"]
        for attrname in ("default", "default_factory", "optional"):
            attrval = getattr(self, attrname)
            if attrval is not MISSING:
                attrs.append(f"{attrname}={attrval!r}")
        attrs_joined = ", ".join(attrs)
        return f"TypeField({attrs_joined})"

    def parse(self, dataval, path):
        if dataval is MISSING:
            dataval = self.get_default(path)
        # TODO: Add type conversion
        return dataval
