import copy
import io
import sys
import warnings
from collections.abc import MutableMapping

from nob.path import Path


class _NobUtils(MutableMapping):
    """Nested OBject manipulation routines"""

    @staticmethod
    def _getitem_slice(func):
        """Decorator for __getitem__ methods to handle slicing"""
        def f(self, key):
            """Handle the cases of [:] and other slice accesses

            If full slice (e.g. [a:b:c]) is used, send it to self._data.
            Lists and strings will work directly, others will fail as expected.
            """
            if type(key) in (slice, int):
                #  detect [:] access. Weird variability... (None/maxsize)
                if key in (slice(None), slice(0, sys.maxsize, None)):
                    return self._data

                # if root is a list, int/slice returns a NobView
                if isinstance(self._data, list):
                    if type(key) == int:
                        return NobView(self._tree, self.root / str(key))
                    return [NobView(self._tree, self.root / str(index))
                            for index in range(*key.indices(len(self._data)))]

                # lastly, try to slice/access the value (works if iterable)
                return self._data[key]
            return func(self, key)
        return f

    def __setitem__(self, key, value):
        """__setitem__ goes directly into the raw data"""
        paths = self._find_all(key)
        if len(paths) > 1:
            raise KeyError(
                f'Key {key} yielded {len(paths)} result(s).\n'
                'You must set a single existing key OR create a new key.\n'
                f'  Results: {paths}')
        if not paths:
            self._data[key] = value
        else:
            path = paths[0]
            if len(path) > 1:
                parent, key = paths[0].split()
                self[parent].__setitem__(key, value)
            else:
                key = path[-1]
                if isinstance(self._data, list):
                    key = int(key)
                self._data[key] = value

    def __delitem__(self, key):
        if type(key) in (slice, int):
            #  detect [:] access. Weird variability... (None/maxsize)
            if key in (slice(None), slice(0, sys.maxsize, None)):
                self.set(None)

            # if root is a list, del like you would a list
            if isinstance(self._data, list):
                del self._data[key]
        else:
            paths = self._find_all(key)
            if len(paths) > 1:
                raise KeyError(
                    f'Key {key} yielded {len(paths)} result(s) instead of'
                    f' exactly 1.\n  Results: {paths}')
            if not paths:
                raise KeyError(f'{key} matches no known key.')
            parent, key = paths[0].split()
            del self._tree._raw_data(self.root / parent)[key]

    def __iter__(self):
        """Dual iterator according to dict or list at root

        If root is a dict, return the iterator on itself.
        To stay consistent, do not iterate on lists, but on a range of the
        list's indices.
        """
        if isinstance(self._data, list):
            yield from range(len(self._data))
        else:
            yield from self._data

    def __getattr__(self, name):
        """Offer attribute access to simplify t.['key'] to t.key"""
        try:
            return self.__getitem__(name)
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        """Offer attribute assignment to simplify t.['key'] = to t.key ="""
        if name in self.__dict__:
            raise AttributeError(f"{name} is a reserved keyword for trees.\n"
                                 "Use full path starting with '/' to access.")
        elif name in 'root paths'.split():
            raise AttributeError(f'{name} is read only.')
        elif name == 'val':
            raise AttributeError(
                "Don't set val, set the tree directly, i.e.:\n"
                "  tree.key = 'value'  (and not tree.key.val = 'value')")
        else:
            paths = self.find(name)
            if len(paths) == 0:
                raise AttributeError(
                    f"{name} does not seem to be a known key.\n"
                    f"To create a new key, please use tree['{name}'] = "
                    f" {value} like you would for a normal dict.")
            elif len(paths) > 1:
                raise AttributeError(
                    f'{name} yielded {len(paths)} result(s).\n'
                    'You must set a single existing key.\n'
                    f'  Results: {paths}')
            self.__setitem__(paths[0], value)

    def __delattr__(self, name):
        try:
            self.__delitem__(name)
        except KeyError as msg:
            raise AttributeError(msg)

    def __eq__(self, value):
        return self._data == value._data

    def __len__(self):
        return len(self._data)

    @property
    def root(self):
        return self._root

    @property
    def paths(self):
        """Dynamically constitute a list of all current valid paths"""
        paths = [Path('/')]

        def rec_walk(root, root_path):
            """Recursive walk of tree"""
            if isinstance(root, dict):
                for key in root:
                    paths.append(root_path / key)
                    rec_walk(root[key], root_path / key)
            elif isinstance(root, list):
                for idx, val in enumerate(root):
                    paths.append(root_path / str(idx))
                    rec_walk(val, root_path / str(idx))

        rec_walk(self._data, Path())
        return paths

    def find(self, key):
        """Find all paths matching key.

        key can be a string (not starting with '/') or an int
        """
        if '/' in str(key):
            raise ValueError(".find only works with a single key, not a path.")
        return [p for p in self.paths if len(p) > 0 and p[-1] == key]
        # Dynamic not implemented yet
        #  if '*' not in address:  # Static address
        #      return [p for p in paths if address in p]
        #  else:                   # Dynamic address
        #      keys = [k for k in address.split('/') if k != '*']
        #      return [p for p in paths
        #              if all([k in p for k in keys])]

    def _find_all(self, identifier):
        """A more robust find that also tolerates full paths"""
        try:
            return self.find(identifier)
        except ValueError:
            return [Path(identifier)]

    def _find_unique(self, identifier):
        """Helper method to ensure unique path is found"""
        paths = self._find_all(identifier)
        if len(paths) != 1:
            raise KeyError(
                f'Identifier {identifier} yielded {len(paths)} result(s) '
                f'instead of 1.\n  Results: {paths}')
        return paths[0]

    @property
    def val(self):
        """Raw data of the nob"""
        warnings.warn(
            ".val access is deprecated, use [:] instead",
            DeprecationWarning
        )
        return self._data

    def copy(self):
        """Return a fully separate copy of current nob"""
        return Nob(copy.deepcopy(self._data))

    def keys(self):
        """Imitate the dict().keys() method"""
        if isinstance(self._data, list):
            return {k: None for k in range(len(self))}.keys()
        return self._data.keys()

    def get(self, key, default=None):
        """Imitate the dict().get() method

        For consistency with default, never return a NobView object, only the
        value associated to key.
        """
        try:
            return self[key][:]
        except KeyError:
            return default

    def np_serialize(self, minsize=0, compress=False):
        """Rewrite all numpy arrays of at least minsize to binary string in place

        This is based on np.save, and is approximately 10% less efficient than
        np.save alone. But with the benefit of conserving structure!

        WARNING: compress=True is quite compact, but takes longer
        WARNING2: numpy scalars are converted to their Python counterpart
        """
        import numpy as np
        if compress:
            import zlib

        def serialize(arr):
            """Serialize a numpy object"""
            memfile = io.BytesIO()
            np.save(memfile, arr)
            memfile.seek(0)
            serial = memfile.read()
            if compress:
                serial = zlib.compress(serial)
            return serial.decode('latin-1')

        for path in self.paths:
            val = self[path][:]
            if isinstance(val, np.ndarray):
                if val.size >= minsize:
                    self[path] = serialize(val)
                else:
                    self[path] = val.tolist()
            elif isinstance(val, np.generic):
                # Why oh why do you use numpy scalars??
                self[path] = val.tolist()

        return self

    def np_deserialize(self):
        """Deserialize all numpy arrays from strings in place

        In practice this reverts np_serialize. Figuring out if string was
        compressed is automatic.
        """
        import numpy as np
        import zlib

        def deserialize(serialized):
            """Deserialize a numpy array"""
            def deser(decompress=False):
                ser = serialized.encode('latin-1')
                ser = zlib.decompress(ser) if decompress else ser
                memfile = io.BytesIO()
                memfile.write(ser)
                memfile.seek(0)
                return np.load(memfile)

            try:
                return deser()
            except ValueError:
                return deser(decompress=True)

        for path in self.paths:
            if isinstance(self[path][:], str):
                try:
                    self[path] = deserialize(self[path][:])
                except (ValueError, zlib.error):
                    continue

        return self

    def reserved(self):
        """View all reserved attributes"""
        return [name for name in dir(self) if name[:2] != '__']


class Nob(_NobUtils):
    """Container class for a nested object

    Nested objects are JSON-valid data: a dict, containing lists and dicts of
    integers, floats and strings.
    """
    def __init__(self, data=None):
        if data is None:
            data = {}
        elif isinstance(data, _NobUtils):
            data = data._data
        self.__dict__['_data'] = data
        self.__dict__['_root'] = Path('/')
        self.__dict__['_tree'] = self

    @_NobUtils._getitem_slice
    def __getitem__(self, key):
        path = self._find_unique(key)
        return NobView(self, path)

    def __str__(self):
        """Printable contents"""
        return str(self._data)

    def __repr__(self):
        """Printable reprensentation"""
        return f'Nob({str(self._data)})'

    def _raw_data(self, path):
        """Access the raw data by path

        path : a Path object

        Handle the issue of alternating between strings (for dicts) and
        integers (for lists).
        """
        tmp = self._data
        for key in path:
            try:
                tmp = tmp[key]
            except TypeError:
                tmp = tmp[int(key)]
        return tmp


class NobView(_NobUtils):
    """View of a Nob object

    Behavec very similarly to its reference Nob object, but all actions
    are performed on the Nob memory directly.
    """
    def __init__(self, tree, path):
        self.__dict__['_tree'] = tree
        self.__dict__['_root'] = tree._find_unique(path)

    @_NobUtils._getitem_slice
    def __getitem__(self, key):
        path = self._find_unique(key)
        return NobView(self._tree, self._root / path)

    def set(self, value):
        """Set the value of self"""
        parent, key = self._root.split()
        self._tree._raw_data(parent)[key] = value

    def __set__(self, instance, value):
        self.set(value)

    def __str__(self):
        """Printable contents"""
        return str(self._data)

    def __repr__(self):
        """Printable reprensentation"""
        return f'NobView:{str(self._root)}'

    # This might be impossible. See issue #1
    # def __del__(self):
    #     self._tree.__delattr__(self._root)

    @property
    def _data(self):
        return self._tree._raw_data(self._root)

    @property
    def parent(self):
        return NobView(self._tree, self._root.parent)


def Tree(*args, **kwargs):
    warnings.warn('Tree object is deprecated. Use Nob instead.')
    return Nob(*args, **kwargs)


def TreeView(*args, **kwargs):
    warnings.warn('TreeView object is deprecated. Use Nob instead.')
    return NobView(*args, **kwargs)
