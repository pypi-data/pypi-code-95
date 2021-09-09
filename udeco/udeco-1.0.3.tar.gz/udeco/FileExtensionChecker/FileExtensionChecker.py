from ..FunctionAnnotationChecker.FunctionAnnotationChecker import _get_default_args



class InvalidExtensionException(Exception):
    """InvalidExtensionException will be raised when arguments file extension is not equal to specified extension."""

    def __init__(self, arg_name: str, valid_extension: str, value: str):
        """
        Arguments:
        ----------
            arg_name {str} -- argument name
            valid_extension {str} -- extension which you want to fixed
            value {str} -- argument value
        """
        msg = f"{arg_name} requires extension {valid_extension}. You specified the argument as {value}"
        super().__init__(msg)


def _sort_argument(*args, **kwargs):
    argument_names = kwargs.get("argument_names")
    del kwargs["argument_names"]

    result = {}
    for arg, name in zip(args, argument_names):
        if name == "self":
            continue

        result[name] = arg

    for k, v in kwargs.items():
        if not k in result:
            result[k] = v

    return result


def extension_checker(**vkwargs):
    """extension_checker checks arguments' file name extension.

    Examples:
    ---------
        >>> @extension_checker(filename="jpg)
        ... def hoge(filename):
        ...     print(filename)
        >>> hoge("hoge.jpg")
        hoge.jpg
        >>> hoge(filename="hoge.jpg")
        hoge.jpg
    """

    accept_none = vkwargs.get("accept_none", False)
    def _check_filename(func):
        func_varnames = list(func.__code__.co_varnames[: func.__code__.co_argcount])
        args_index = {k: i for i, k in enumerate(func_varnames)}
        default_args = _get_default_args(func)

        def wrapper(*args, **kwargs):
            kwargs.update(default_args)
            arguments = _sort_argument(*args, **kwargs, argument_names=list(func.__code__.co_varnames))

            for varname, extension in vkwargs.items():
                if varname == "accept_none":
                    continue

                if arguments[varname] is None and accept_none:
                    continue

                ext = arguments[varname].split(".")[-1]
                if not ext == extension:
                    raise InvalidExtensionException(
                        varname, extension, arguments[varname]
                    )

            if func_varnames[0] == "self":
                arguments["self"] = args[0]

            return func(**arguments)

        return wrapper

    return _check_filename
