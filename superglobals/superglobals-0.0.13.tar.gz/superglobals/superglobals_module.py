import inspect

def superglobals():
    _globals = dict(inspect.getmembers(
                inspect.stack()[len(inspect.stack()) - 1][0]))["f_globals"]
    return _globals

def _dotted(key):
    key = key.replace(r'\.', 'PSIOUFJRHPRIUENG')
    pieces = key.split('.')
    return [x.replace('PSIOUFJRHPRIUENG', '.') for x in pieces]

def _ensure_path(_dict, path, test=False):
    for piece in path:
        if piece not in _dict or not isinstance(_dict[piece], dict):
            if test:
                return None
            _dict[piece] = dict()
        _dict = _dict[piece]
    return _dict


def _base(key, test=False):
    _globals = superglobals()

    if isinstance(key, list):
        path = key
    else:
        path = _dotted(key)

    if len(path) == 1:
        return _globals

    base = _ensure_path(_globals, path[0:-1], test=test)
    return base

def hasglobal(key):
    """
    hasglobal(name) -> bool

    Return whether the global variable `key` exists
    """
    path = _dotted(key)
    base = _base(path, test=True)
    if base is not None:
        return path[-1] in base

def getglobal(key, default=None, _type=None):
    """
    getglobal(key[, default]) -> value
    
    Return the value for key if key is in the global dictionary, else default.
    """
    path = _dotted(key)
    base = _base(path, test=True)
    if isinstance(base, dict):
        return base.get(path[-1], default)
    return default
    #  return superglobals().get(key, default)

def setglobal(key, value):
    path = _dotted(key)
    base = _base(path, test=False)
    if not isinstance(base, dict):
        raise TypeError("globals::{} was not a dict".format('.'.join(key[0:-1])))
    base[path[-1]] = value

def defaultglobal(key, value):
    """
    defaultglobal(key, value)

    Set the value of global variable `key` if it is not otherwise set and
    return the new/existing contents of the global variable
    """
    path = _dotted(key)
    base = _base(path, test=False)
    if not isinstance(base, dict):
        raise TypeError("globals::{} was not a dict".format('.'.join(key[0:-1])))
    if path[-1] not in base:
        base[path[-1]] = value
        return base[path[-1]]
    return base.get(path[-1])
