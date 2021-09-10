from typing import Any, Tuple

from annotell.openlabel.models.data_types import Boolean, DataTypeBase, Num, Text, Vec


def get_openlabel_type(name: str, val: Any) -> Tuple[str, DataTypeBase]:

    def isfloat(num: str) -> bool:
        try:
            float(num)
            return True
        except:  # noqa:E722
            return False

    if isinstance(val, bool):
        return "boolean", Boolean(name=name, val=val)
    elif isinstance(val, list):
        return "vec", Vec(name=name, val=val)
    elif isinstance(val, str):
        return "text", Text(name=name, val=val)
    elif isinstance(val, int):
        return "num", Num(name=name, val=val)
    elif isfloat(val):
        return "num", Num(name=name, val=float(val))

    raise NotImplementedError
