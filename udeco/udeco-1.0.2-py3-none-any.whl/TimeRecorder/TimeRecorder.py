import time
import numpy as np

_print_orig = print


def timer(iteration: int = 1, result_index: int = 0, print_only_first: bool = True):
    def _timer(func):
        def wrapper(*args, **kwargs):
            result = []
            result_append = result.append
            dt = []
            dt_append = dt.append

            def do_nothing(*args, **kwargs):
                pass

            for i in range(iteration):
                if print_only_first and i > 0:
                    globals()["print"] = do_nothing

                st = time.time()
                result_append(func(*args, **kwargs))
                et = time.time()
                dt_append(et - st)

            globals()["print"] = _print_orig

            dt = np.array(dt)

            print(f"Average process time: {np.average(dt)}")
            print(f"Max process time    : {dt.max()}")
            print(f"Minumin process time: {dt.min()}")

            return result[result_index]

        return wrapper

    return _timer
