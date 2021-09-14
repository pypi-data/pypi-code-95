class HydeCallable:
    arity = -1

    def call(self, interpreter, arguments):
        raise NotImplementedError
