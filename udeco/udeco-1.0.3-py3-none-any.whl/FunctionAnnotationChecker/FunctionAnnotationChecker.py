from typing import Union, Any
import inspect


class InvalidArgumentTypeException(Exception):
    def __init__(self, arg_name: str, valid_type: Any, value: Any):
        mes = f"{arg_name} requires type {valid_type}. You specified the argument as {value}"
        super().__init__(mes)


class InvalidReturnTypeException(Exception):
    def __init__(self, valid_type: Any, value: Any):
        mes = f"Return values requires type {valid_type}. Function tried ti return values as {value}"
        super().__init__(mes)


def _get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def annotation_checker(func):
    annotations = func.__annotations__
    return_type = annotations["return"]
    func_varnames = list(func.__code__.co_varnames[: func.__code__.co_argcount])
    func_varnames_keys = {k: i for i, k in enumerate(func_varnames) if k in annotations}

    def wrapper(*args, **kwargs):
        annotations_list = [k for k in annotations.keys()]
        annotations_list.remove("return")

        for k, v in kwargs.items():
            if k in annotations:
                if not isinstance(v, annotations[k]):
                    raise InvalidArgumentTypeException(k, annotations[k], type(v))

                annotations_list.remove(k)

        default_args = _get_default_args(func)
        for annotation in annotations_list:
            if (
                func_varnames_keys[annotation] >= len(args)
                and annotation in default_args
            ):
                if not isinstance(default_args[annotation], annotations[k]):
                    raise InvalidArgumentTypeException(
                        annotation, annotations[annotation], default_args[annotation]
                    )
            else:
                value = args[func_varnames_keys[annotation]]
                if not isinstance(value, annotations[annotation]):
                    raise InvalidArgumentTypeException(
                        annotation, annotations[annotation], type(value)
                    )

        result = func(*args, **kwargs)
        result_type = type(result)

        # In the case of return value is Union
        if "Union" in str(return_type):
            args = return_type.__args__
            if not result_type in args:
                raise InvalidReturnTypeException(args, return_type)
            assert result_type in args

        else:
            assert result_type == return_type

        return result

    return wrapper
