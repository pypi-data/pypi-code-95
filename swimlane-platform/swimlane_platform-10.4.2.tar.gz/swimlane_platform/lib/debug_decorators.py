import functools

def funccode(func):
    try:
        return func.func_code
    except AttributeError:
        return func.__code__

def funcname(func):
    try:
        return func.func_name
    except AttributeError:
        return func.__name__

def info_function_start_finish(action_description=None):

    def wrap(func):
        action = action_description if action_description else funcname(func).replace('_', ' ') + '.'

        @functools.wraps(func)
        def echo_func(*args, **kwargs):
            if args[0] and hasattr(args[0], 'logger'):
                logger = args[0].logger
                logger.info('Starting {action}'.format(action=action))
                result = func(*args, **kwargs)
                logger.info('Finishing {action}'.format(action=action))
                return result
            else:
                return func(*args, **kwargs)

        return echo_func
    return wrap


def verbose_function_start_finish(action_description=None):

    def wrap(func):
        action = action_description if action_description else funccode(func).replace('_', ' ') + '.'

        @functools.wraps(func)
        def echo_func(*args, **kwargs):
            if args[0] and hasattr(args[0], 'logger'):
                logger = args[0].logger
                try:
                    logger.verbose('Starting {action}'.format(action=action))
                    result = func(*args, **kwargs)
                    logger.verbose('Finishing {action}'.format(action=action))
                    return result
                except AttributeError:
                    pass
            return func(*args, **kwargs)

        return echo_func
    return wrap


def debug_function_args(func):
    arg_names = funccode(func).co_varnames[:funccode(func).co_argcount]
    function_name = funcname(func)

    @functools.wraps(func)
    def echo_func(*args, **kwargs):
        if args[0] and hasattr(args[0], 'logger'):
            logger = args[0].logger
            names = arg_names[1:]
            values = args[1:]
            asterisk = []
            if len(names) < len(values):
                asterisk = [('*', values[len(names):])]
            args_with_values = ', '.join('%s=%r' % entry for entry in list(zip(names, values)) + asterisk + list(kwargs.items()))
            logger.debug('{name} called with {args}'.format(name=function_name, args=args_with_values))

        return func(*args, **kwargs)

    return echo_func


def debug_function_return(func):
    function_name = funcname(func)

    @functools.wraps(func)
    def echo_func(*args, **kwargs):
        if args[0]and hasattr(args[0], 'logger'):
            logger = args[0].logger
            result = func(*args, **kwargs)
            logger.debug('{name} returned {result}'.format(name=function_name, result=result))
            return result
        else:
            return func(*args, **kwargs)

    return echo_func
