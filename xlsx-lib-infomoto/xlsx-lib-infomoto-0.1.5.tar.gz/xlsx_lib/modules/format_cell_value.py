from typing import Optional


def format_cell_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    value = str(value) \
        .lstrip() \
        .rstrip() \
        .replace("b'", "") \
        .replace("'", "")

    if value in ["-"]:
        return None

    for replaced in ["   ", "  ", ]:
        value = value.replace(replaced, " - ")

    # TODO: To dict replace
    if "OHMIOS" in value:
        value = value.replace("OHMIOS", "Ω")

    return value
