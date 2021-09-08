import importlib
import json
import os

with importlib.resources.open_text("designer", "colors.json") as f:
    colors = json.load(f)
    f.close()

def _process_color(color) -> 'List[int]':
    """
    Converts either a color string (e.g., 'orange') into a color triplet (list of 3 numbers).
    If a color triplet is passed in, it is returned unmodified.

    :param color:
    :return:
    """
    if isinstance(color, str):
        return colors[color]
    else:
        return color
