from typing import Mapping as _abc_Mapping

from ._typed import Typed


# Integer
class Integer(Typed):
    expected_type = int


# Float
class Float(Typed):
    expected_type = float


# String
class String(Typed):
    expected_type = str


# List
class List(Typed):
    expected_type = list


# Mapping
class Mapping(Typed):
    expected_type = _abc_Mapping


# Tuple
class Tuple(Typed):
    expected_type = tuple
