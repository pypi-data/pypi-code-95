# --------------------------------------------------------------------------------------
# File: "MultiprocessingFunctions.py"
# Dir: "SandsPythonFunctions\src\SandsPythonFunctions"
# Created: 2020-05-25
# --------------------------------------------------------------------------------------

"""
this file is meant to allow for easy use multiprocessing in python for functions that
can benifit from using multiple cores

TESTCODE: designates code used in testing the script
make sure to comment out that   line so that it does not impact the production code
"""

'''
def multiprocessing_pool(
    input_function, iterable_list=list, process_number=2, extra_arg=""
):
    """this function processes a function over a list of objects concurrently using the
    multiprocessing.Pool module

    Arguments:
        input_function {function} -- the function that you want to process concurrently
        iterable_list {list} -- this has to be a list of objects that you want to


    Keyword Arguments:
        process_number {int} -- number of threads to use (default: {2})
        extra_arg {str} -- if you have extra arguments for the function that is being
            processed concurrently (default: {""})

    Returns:
        list -- this returns a list of objects that are returned from the processing
    """
    import itertools
    from multiprocessing import Pool

    with Pool(processes=process_number) as pool:
        if extra_arg == "":
            output_list = pool.map(input_function, iterable_list)
        else:
            if len(extra_arg) == 1:
                extra_arg = extra_arg[0]
            output_list = pool.starmap(
                input_function, zip(iterable_list, itertools.repeat(extra_arg))
            )
    return output_list
'''


def concurrent_pool(
    input_function, iterable_list, process_number=2, extra_arg="", timeout=(5 * 60)
):
    """this function processes a function over a list of objects concurrently using the
    concurrent.futures.ProcessPoolExecutor module

    Arguments:
        input_function {function} -- the function that you want to process concurrently

        iterable_list {list} -- this has to be a list of objects that you want to

    Keyword Arguments:
        process_number {int} -- number of threads to use (default: {2})

        extra_arg {str} -- only enter one extra argument can be any type (default: {""})

        timeout {int} -- time in seconds you want to wait before the function terminates
        (default: 5 minutes)

    Returns:
        list -- this returns a list of objects that are returned from the processing
    """
    import itertools
    import concurrent.futures as cf

    if extra_arg == "":
        with cf.ProcessPoolExecutor(max_workers=process_number) as executor:
            output_list = executor.map(input_function, iterable_list, timeout=timeout)
    else:
        with cf.ProcessPoolExecutor(max_workers=process_number) as executor:
            output_list = executor.map(
                input_function,
                iterable_list,
                itertools.repeat(extra_arg),
                timeout=timeout,
            )
    return list(output_list)
