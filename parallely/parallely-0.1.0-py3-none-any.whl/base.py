class ParalellyFunction:
    def __init__(self, func, max_workers):
        self._func = func
        self._max_workers = max_workers

    def map(self, *args, **kwargs):
        raise NotImplementedError("All children should implement map")

    def _execute_once(self, *args, **kwargs):
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        return self._execute_once(*args, **kwargs)
