import os, json, atexit

from .functions import _get_vars


class State:
    def __init__(self, default: dict = None, **kwargs):
        file, = _get_vars([
            ('file', 'STATE_FILE')
        ], kwargs)

        if default is None:
            default = {}
        elif type(default) is not dict:
            raise TypeError('default must be dictionary')

        if not os.path.exists(file):
            self._data = default
        else:
            with open(file, 'r') as f:
                self._data = json.loads(f.read())

        self._file = file
        atexit.register(self.__cleanup)

    def __cleanup(self):
        if hasattr(self, '_file'):
            with open(self._file, 'w') as f:
                f.write(json.dumps(self._data))
        atexit.unregister(self.__cleanup)

    def __del__(self):
        if 'open' in __builtins__:
            self.__cleanup()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        if key in self._data:
            del self._data[key]