from typing import Set

import numpy as np
from terality_serde import StructType

from . import ClassMethod, Struct, StructIterator


class ClassMethodNDArray(ClassMethod):
    _class_name: str = StructType.NDARRAY
    _pandas_class = np.ndarray
    _additional_class_methods: Set[str] = {"from_numpy"}


class NDArray(Struct, metaclass=ClassMethodNDArray):
    """
    np.ndarray distributed version. This class aims to
    be able to manipulate ndarray during pandas workflow,
    but numpy API is not supported.
    Thus, any method call on an NDArray instance will fail,
    and the constructor is not provided.
    """

    _pandas_class_instance = np.empty(0)
    _additional_methods: Set[str] = {"to_numpy"}
    _indexers: Set[str] = set()

    def __iter__(self):
        return StructIterator(self)
