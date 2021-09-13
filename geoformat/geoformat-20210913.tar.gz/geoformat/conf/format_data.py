import string


def value_to_iterable_value(value, output_iterable_type=list):
    """
    Transform value to iterate value (list by default)

    :param value: value that we want to transfomr
    :param output_iterable_type: iterable type to transform
    :return: input value transform to given (by iterable_type) iterable value type
    """

    # check if iterable type if iterable
    if output_iterable_type not in {list, tuple, set}:
        raise Exception("output_iterable_type must be list, tuple or set")

    # make type transform
    if value is not None:
        # if output type is same that input
        if isinstance(value, output_iterable_type):
            output_value = value
        else:
            # if input type is yet iterable
            if isinstance(value, (list, tuple, set)):
                value = list(value)
            else:
                # if not make it iterable
                value = [value]
            # transform input type
            output_value = output_iterable_type(value)
    else:
        output_value = None

    return output_value


def is_hexadecimal(s):
    """
    Check if input string value is hexadecimal or not

    :param s: input string
    :return: True if hexadecimal / False if not hexadecimal
    """
    hex_digits = set(string.hexdigits)
    # if s is long, then it is faster to check against a set
    return all(c in hex_digits for c in s)


def pairwise(iterable):
    """
    from https://stackoverflow.com/questions/5764782/iterate-through-pairs-of-items-in-a-python-list?lq=1
    iterable = [s0, s1, s2, s3, ...]
    return ((s0,s1), (s1,s2), (s2, s3), ...)

    """
    import itertools

    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)
