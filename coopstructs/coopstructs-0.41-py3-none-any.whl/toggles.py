from typing import List, Callable, Any

class Toggleable():
    def __init__(self, values: List, starting_index: int = 0):
        # TODO: Values is better as a generator. This allows for user to provide an "infinite" list and not provide all values to memory
        self.values = values
        self.index = starting_index

    def toggle(self, on_toggle_callback: Callable[[Any], Any] = None):
        self.index += 1

        if self.index >= len(self.values):
            self.index = 0

        if on_toggle_callback is not None:
            on_toggle_callback()

        return self.value

    @property
    def value(self):
        return self.values[self.index]

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def copy(self):
        return type(self)(values=self.value, starting_index=self.index)

    def set_value(self, value):
        self.index = self.values.index(value)

class BooleanToggleable(Toggleable):
    def __init__(self, default: bool = True):
        if default:
            index = 1
        else:
            index = 0

        Toggleable.__init__(self, [False, True], index)

    @property
    def is_on(self):
        return self.value

    def copy(self):
        default = True if self.index == 1 else False
        return type(self)(default=default)

    def __add__(self, other):
        return any([self.value, other.value])

    def __gt__(self, other):
        if self.value and not other.value:
            return True
        else:
            return False

    def __ge__(self, other):
        if self.value or self.value == other.value == False:
            return True
        else:
            return False

    def __le__(self, other):
        if other.value or self.value == other.value == False:
            return True
        else:
            return False

    def __lt__(self, other):
        if not self.value and other.value:
            return True
        else:
            return False

class IntegerRangeToggleable(Toggleable):
    def __init__(self, min: int, max: int, step_size: int = 1):
        Toggleable.__init__(self, [ii for ii in range(min, max+1, step_size)])

        self.min = min
        self.max = max
        self.step = step_size


    def copy(self):
        return type(self)(min=self.min, max=self.max, step_size=self.step)

class EnumToggleable(Toggleable):
    def __init__(self, enum_type, default=None):
        self.enum = enum_type
        Toggleable.__init__(self, [val for val in enum_type.__members__.values()], 0)
        if default is not None:
            self.set_value(default)