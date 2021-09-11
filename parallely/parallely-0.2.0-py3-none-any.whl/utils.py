from itertools import repeat


def is_iterator(obj):
    return hasattr(obj, "__iter__")


def prepare_arguments(arg_list, kwarg_list):
    arg_generator = []
    kwarg_generator = {}

    min_length = 1e20
    for arg in arg_list:
        if is_iterator(arg):
            min_length = min(len(arg), min_length)
            arg_generator.append(iter(arg))
        else:
            arg_generator.append(repeat(arg))

    for key, arg in kwarg_list.items():
        if is_iterator(arg):
            min_length = min(len(arg), min_length)
            kwarg_generator[key] = iter(arg)
        else:
            kwarg_generator[key] = repeat(arg)

    if min_length == 1e20 or min_length == 0:
        raise ValueError(arg_list, kwarg_list)

    args, kwargs = [], []
    for i in range(min_length):
        arg_row = [next(arg_gen) for arg_gen in arg_generator]
        args.append(arg_row)

        kwarg_row = {key: next(arg_gen) for key, arg_gen in kwarg_generator.items()}
        kwargs.append(kwarg_row)

    return args, kwargs
