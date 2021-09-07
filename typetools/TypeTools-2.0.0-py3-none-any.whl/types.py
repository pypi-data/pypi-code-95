from .typed import Typed


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


# Dict
class Dict(Typed):
    expected_type = dict


# Tuple
class Tuple(Typed):
    expected_type = tuple
