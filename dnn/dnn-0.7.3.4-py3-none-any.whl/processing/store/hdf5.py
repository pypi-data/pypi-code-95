import h5py
import os

class HDF5DatasetWriter:
    def __init__(self, output, scheme = None, buf_size = 100):
        self.buf_size = buf_size
        self.buffer = {}
        self.db = None
        self.idx = 0
        self._current_buf_size = 0
        self.db = h5py.File (output, "w")
        if scheme:
            for name, (dims, dtype) in scheme.items ():
                self.dataset (name, dims, dtype)

    def dataset (self, name, dims, dtype = 'float'):
        self.db.create_dataset (name, dims, dtype = dtype)
        self.buffer [name] = []

    def __enter__ (self, *args, **kargs):
        return self

    def __exit__ (self, *args, **kargs):
        self.close ()

    def add (self, **data):
        for k, v in data.items ():
            self.buffer [k].append (v)
        self._current_buf_size += 1
        if self._current_buf_size >= self.buf_size:
            self.flush ()

    def flush (self):
        new_data_index = self.idx + self._current_buf_size
        for k, v in self.buffer.items ():
            self.db [k][self.idx : new_data_index] = v
        self.idx, self._current_buf_size = new_data_index, 0
        for k in self.buffer:
            self.buffer [k] = []

    def close (self):
        if self._current_buf_size:
            self.flush ()
        self.buffer = None
        self.db.close ()
        self.db = None


class HDF5DatasetReader:
    def __init__ (self, path):
        self.db = h5py.File(path, 'r')

    def __enter__ (self, *args, **kargs):
        return self

    def __exit__ (self, *args, **kargs):
        self.db.close ()

    def __getattr__ (self, name):
        return getattr (self.db, name)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return { k: self.db [k][item] for k in self.db.keys () }
        else:
            return self.db.__getitem__(item)


def open (path, mode = 'r', scheme = None, buf_size = 100):
    if mode == 'w':
        return HDF5DatasetWriter (path, scheme, buf_size)
    assert scheme is None
    return HDF5DatasetReader (path)