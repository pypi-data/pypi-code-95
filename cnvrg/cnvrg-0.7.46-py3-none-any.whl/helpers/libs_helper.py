from importlib.util import find_spec

def check_if_lib_exists(lib):
    spec = find_spec(lib)
    return spec is not None