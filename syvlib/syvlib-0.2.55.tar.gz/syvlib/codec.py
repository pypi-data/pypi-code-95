from io import BytesIO
from functools import reduce
from operator import mul
import struct

import numpy as np


def encode(array: np.ndarray, byteorder: str = 'big') -> bytes:

    stream = BytesIO()
    fsp = '>' if byteorder == 'big' else '<'

    # shape_len
    # 1 byte
    stream.write(struct.pack(fsp+'B', len(array.shape)))

    # shape
    # (shape_len * 4) bytes
    stream.write(struct.pack(fsp+str(len(array.shape))+'I', * array.shape))

    # dtype_code
    # 1 byte
    stream.write(array.dtype.char.encode('utf-8'))
    dtype = array.dtype.newbyteorder(byteorder)

    # data_len
    # 8 bytes
    data_len = (reduce(mul, array.shape) * array.dtype.itemsize)
    stream.write(struct.pack(fsp+'Q', data_len))

    # data
    # (data_len) bytes
    stream.write(array.astype(dtype).tobytes())

    return stream.getvalue()


def decode(data: bytes, byteorder: str = 'big') -> np.ndarray:

    stream = BytesIO(data)
    fsp = '>' if byteorder == 'big' else '<'

    # shape_len
    # 1 byte
    shape_len = struct.unpack(fsp+'B', stream.read(1))[0]

    # shape
    # (shape_len * 4) bytes
    shape = struct.unpack(fsp+str(shape_len)+'I', stream.read(shape_len*4))

    # dtype_code
    # 1 byte
    dtype_code = stream.read(1).decode('utf-8')
    dtype = np.dtype(dtype_code).newbyteorder(byteorder)

    # data_len
    # 8 bytes
    data_len = struct.unpack(fsp+'Q', stream.read(8))[0]

    # data
    # (data_len) bytes
    array = np.frombuffer(stream.read(data_len), dtype)

    return array.reshape(shape).astype(np.dtype(dtype_code))
