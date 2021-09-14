from hyde.hyde_callable import HydeCallable


class Globals:
    class GlobalHydeCallable(HydeCallable):
        def __str__(self):
            return f'<fn {self.__name__}'


    class Clock(GlobalHydeCallable):
        from time import time

        arity       = 0

        def call(self, _interpreter, _arguments):
            return round(self.time() * 1000)

    GLOBAL_FUNCTIONS = [
        Clock
    ]

    @classmethod
    def define(cls, environment):
        for fn in cls.GLOBAL_FUNCTIONS:
            environment.define(fn.__name__.lower(), fn())