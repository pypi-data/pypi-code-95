import json

import rend.exc


__virtualname__ = "json"


def render(hub, data):
    """
    Render the given json data
    """
    try:
        if isinstance(data, (str, bytes, bytearray)):
            ret = json.loads(data)
        else:
            ret = json.load(data)
    except json.decoder.JSONDecodeError as exc:
        raise rend.exc.RenderException(f"Json render error: {exc.msg}")
    return ret
