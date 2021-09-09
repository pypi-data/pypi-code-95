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

    def _check_filename(func):
        func_varnames = list(func.__code__.co_varnames[: func.__code__.co_argcount])
        args_index = {k: i for i, k in enumerate(func_varnames)}

        def wrapper(*args, **kwargs):
            for varname, extension in vkwargs.items():
                if varname in kwargs:
                    if not kwargs[varname].split(".")[-1] == extension:
                        raise InvalidExtensionException(
                            varname, extension, kwargs[varname]
                        )

                elif varname in func_varnames:
                    idx = args_index[varname]
                    if not args[idx].split(".")[-1] == extension:
                        raise InvalidExtensionException(varname, extension, args[idx])

            return func(*args, **kwargs)

        return wrapper

    return _check_filename
