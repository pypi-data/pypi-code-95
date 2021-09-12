from typing import Any, Callable

from numpy.core.fromnumeric import nonzero


class WBool:
    'Boolean that explains why_false and calls hook when failed to assert'
    value: bool
    why_false: str
    hook: Callable[[], Any]

    def __bool__(self):
        return self.value

    def assert_explain(self):
        if not self:
            try:
                self.hook()
            except:
                pass
            raise AssertionError(self.why_false)

    def __str__(self):
        return 'True' if self else f'False: {self.why_false}'


class WBools:
    'Class with WBool factory and describe methods'

    def _wbool(self, value: bool, why_false=None):
        'Boolean that describes self when failed to require'
        r = WBool()
        r.value = bool(value)
        r.why_false = why_false
        r.hook = lambda: self.describe()
        return r

    def describe(self):
        pass
