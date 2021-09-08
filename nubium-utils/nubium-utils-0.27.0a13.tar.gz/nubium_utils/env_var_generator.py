def env_vars_creator(dict_func):
    """
    Allows you to call a dict without constantly re-instantiating it or assigning it to a constant.
    The dict is not created until you evaluate the return of this function (another function) for the first time.
    Every subsequent evaluation of the returned function will return the previously created dict (it's just getting
    the same dict via an infinite generator).

    This allows you to avoid having a dict constant, which would cause import failures at init time if you are missing
    any of the required environment variables. This is mostly relevant with regards to unit tests, where some env vars
    may not be defined until during/after setup.
    """
    def get_generator(dict_func):
        d = dict_func()
        while True:
            yield d

    def get_dict(dict_func):
        gen = get_generator(dict_func)
        return lambda: next(gen)

    return get_dict(dict_func)
