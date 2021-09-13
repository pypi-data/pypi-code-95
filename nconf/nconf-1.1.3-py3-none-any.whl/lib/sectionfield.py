from .missing import MISSING
from .field import Field


class SectionField(Field):
    def __init__(self, field_type, fields, /, *, default=MISSING, default_factory=MISSING, optional: bool = False):
        super().__init__(default, default_factory, optional)
        self.type: type = field_type
        self.subfields: dict[str, Field] = fields

    def __repr__(self):
        attrs = [
            f"cls={self.type.__name__}",
            f"subfields={self.subfields!r}"
        ]
        for attrname in ("default", "default_factory", "optional"):
            attrval = getattr(self, attrname)
            if attrval is not MISSING:
                attrs.append(f"{attrname}={attrval!r}")
        attrs_joined = ", ".join(attrs)
        return f"SectionField({attrs_joined})"

    def parse(self, dataval: dict, path: str, obj=None):
        if obj is None:
            obj = self.type()
        if dataval is MISSING:
            return self.get_default(path)
        for name, f in self.subfields.items():
            subpath = f"{path}.{name}"
            subdataval = dataval.get(name, MISSING)
            parsed = f.parse(subdataval, subpath)
            if parsed is not MISSING:
                setattr(obj, name, parsed)
        return obj
