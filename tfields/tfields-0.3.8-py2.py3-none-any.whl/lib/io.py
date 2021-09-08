import typing
import ast
import sys
import importlib
import base64
import numpy as np


def get_module_and_name(type_) -> typing.Tuple[str, str]:
    """
    Examples:
        >>> import numpy as np

        This function can be used to ban your type to file as a string and (with the get_type
        method) get it back.
        >>> [get_type(*get_module_and_name(type_)) for type_ in (int, np.ndarray, str)]
        [<class 'int'>, <class 'numpy.ndarray'>, <class 'str'>]
    """
    return sys.modules[type_.__module__].__name__, type_.__qualname__


def get_type(module, name):
    """
    Inverse to :fun:`get_module_and_name`
    """
    importlib.import_module(module)
    return getattr(sys.modules[module], name)


def numpy_to_str(arr):
    """
    Convert an array to string representation

    Examples
        >>> import numpy as np
        >>> arr = np.array([[1,2,3], [1,4,5]])
        >>> enc = numpy_to_str(arr)
        >>> str_to_numpy(enc)
        array([[1, 2, 3],
               [1, 4, 5]])
    """
    arr = np.ascontiguousarray(arr)
    str_rep = base64.binascii.b2a_base64(arr).decode("ascii").rstrip("\n")
    shape = arr.shape
    dtype = arr.dtype
    str_ = f"{str_rep}::{shape}::{dtype}"
    return str_


def str_to_numpy(str_):
    """
    Convert back from numpy_to_str
    """
    str_rep, shape, dtype = str_.split("::")
    dtype = getattr(np, dtype)
    arr = np.frombuffer(
        base64.binascii.a2b_base64(str_rep.encode("ascii")), dtype=dtype
    )
    arr = arr.reshape(ast.literal_eval(shape))
    return arr


def numpy_to_bytes(arr: np.array) -> bytearray:
    """
    Convert to bytest array

    Examples:
        >>> a = np.ones((23, 23), dtype = 'int')
        >>> a_b = numpy_to_bytes(a)
        >>> a1 = bytes_to_numpy(a_b)
        >>> assert np.array_equal(a, a1) and a.shape == a1.shape and a.dtype == a1.dtype
    """
    arr_dtype = bytearray(str(arr.dtype), "utf-8")
    arr_shape = bytearray(",".join([str(a) for a in arr.shape]), "utf-8")
    sep = bytearray("|", "utf-8")
    arr_bytes = arr.ravel().tobytes()
    to_return = arr_dtype + sep + arr_shape + sep + arr_bytes
    return to_return


def bytes_to_numpy(serialized_arr: bytearray) -> np.array:
    """
    Convert back from numpy_to_bytes
    """
    sep = "|".encode("utf-8")
    i_0 = serialized_arr.find(sep)
    i_1 = serialized_arr.find(sep, i_0 + 1)
    arr_dtype = serialized_arr[:i_0].decode("utf-8")
    arr_shape = tuple(
        int(a) for a in serialized_arr[i_0 + 1 : i_1].decode("utf-8").split(",")
    )
    arr_str = serialized_arr[i_1 + 1 :]
    arr = np.frombuffer(arr_str, dtype=arr_dtype).reshape(arr_shape)
    return arr
