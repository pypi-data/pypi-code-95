import time
import inspect

from geoformat.conf.timer import Timer


def timeit(func):

    def timed(*args, **kw):
        ts = time.time()
        result = func(*args, **kw)
        te = time.time()
        execute_time = te - ts
        current_function_name = func.__name__

        if 'log_time' in kw:
            function_timer = kw['log_time']
            if function_timer:
                for stac in reversed(inspect.stack()):
                    if stac.function not in {'timed', '<module>'}:
                        if stac.function in function_timer.get_children_name():
                            function_timer = function_timer.get_child_timer(child_name=stac.function)
                        else:
                            # create new Timer
                            child_timer = Timer(timer_name=stac.function)
                            # put Timer in child
                            function_timer.add_child_timer(child_timer_object=child_timer)
                            function_timer = function_timer.get_child_timer(stac.function)

                if current_function_name in function_timer.function_in_it:
                    child_timer = function_timer.get_child_timer(current_function_name)
                    child_timer.add_time(execute_time=execute_time)
                else:
                    child_timer = Timer(timer_name=current_function_name)
                    child_timer.add_time(execute_time=execute_time)
                    # save child in parent timer
                    function_timer.add_child_timer(child_timer_object=child_timer)

                # compute decorator time
                decorator_time = time.time() - te
                child_timer.add_decorator_time(execute_time=decorator_time)



        else:
            print('{current_function_name} : {execute_time} ms'.format(
                    current_function_name=current_function_name,
                    execute_time=execute_time*1000
                )
            )

        return result

    return timed

