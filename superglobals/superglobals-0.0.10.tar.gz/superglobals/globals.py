import inspect

def superglobals_():
    _globals = dict(inspect.getmembers(
                inspect.stack()[len(inspect.stack()) - 1][0]))["f_globals"]
    return _globals

def getglobal(key, default=None):
    """
    getglobal(key[, default]) -> value
    
    Return the value for key if key is in the global dictionary, else default.
    """
    _globals = dict(inspect.getmembers(
                inspect.stack()[len(inspect.stack()) - 1][0]))["f_globals"]
    return _globals.get(key, default)

def setglobal(key, value):
    _globals = superglobals_()
    _globals[key] = value

def defaultglobal(key, value):
    """
    defaultglobal(key, value)

    Set the value of global variable `key` if it is not otherwise st
    """
    _globals = superglobals_()
    if key not in _globals:
        _globals[key] = value
