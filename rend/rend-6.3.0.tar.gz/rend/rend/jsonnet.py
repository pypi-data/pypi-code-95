"""
Render jsonnet data
"""
import tempfile

try:
    import _jsonnet

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


async def render(hub, data):
    """
    Render the given data through jsonnet
    """

    if hasattr(data, "read"):
        data = data.read()

    if isinstance(data, bytes):
        fp = tempfile.NamedTemporaryFile("wb+", delete=True)
    else:
        fp = tempfile.NamedTemporaryFile("w+", delete=True)

    # Write bytes to temporary file
    fp.write(data)
    fp.flush()
    ret = _jsonnet.evaluate_file(fp.name)
    fp.close()

    return hub.rend.json.render(ret)
