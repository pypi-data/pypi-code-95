from typing import GenericAlias

from .missing import MISSING
from .field import Field


class ListField(Field):
    def __init__(self, field_type=None, subfield=None, /, *, default=MISSING, default_factory=MISSING, optional: bool = False):
        super().__init__(default, default_factory, optional)
        self.type: GenericAlias = field_type
        self.subfield: Field = subfield

    def __repr__(self):
        attrs = [
            f"type={self.type.__name__}",
            f"subfield={self.subfield!r}"
        ]
        for attrname in ("default", "default_factory", "optional"):
            attrval = getattr(self, attrname)
            if attrval is not MISSING:
                attrs.append(f"{attrname}={attrval!r}")
        attrs_joined = ", ".join(attrs)
        return f"ListField({attrs_joined})"

    def parse(self, dataval, path: str):
        if dataval is MISSING:
            dataval = self.get_default()
        return [self.subfield.parse(d, f"{path}[{i}]") for i, d in enumerate(dataval)]
