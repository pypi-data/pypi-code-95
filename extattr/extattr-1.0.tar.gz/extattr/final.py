from exceptions import FinalException


class final:
    def __init__(self, can_throws: bool = False):
        self._can_throws = can_throws
        self._extattr_declared = {}

    def __call__(self, key_: str, value_=None):
        if value_ is not None:
            return self._set(key_, value_)
        for i in self._extattr_declared.items():
            if i[0] == key_:
                return i[1]
        if self._can_throws:
            raise FinalException("Not found key!")

    def _set(self, key_: str, value_: str) -> str:
        if key_ in self._extattr_declared:
            if self._can_throws:
                raise FinalException("Your can not replace final value/values!")
            return value_
        self._extattr_declared[key_] = value_
        return value_
