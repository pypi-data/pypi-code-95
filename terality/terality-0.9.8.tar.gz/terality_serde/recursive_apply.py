from asyncio import gather
from typing import Any, Callable


def apply_func_on_object_recursively(obj: Any, f: Callable, apply_key_dict: bool = False) -> Any:
    """Recursively apply a callable to a JSON-like tree of objects (i.e. a combination of dictionaries and lists)"""
    if isinstance(obj, list):
        return [apply_func_on_object_recursively(value, f, apply_key_dict) for value in obj]
    if isinstance(obj, tuple):  # pylint: disable=no-else-return
        return tuple(  # pylint: disable=consider-using-generator
            [apply_func_on_object_recursively(value, f, apply_key_dict) for value in obj]
        )
    elif isinstance(obj, dict):
        return {
            apply_func_on_object_recursively(key, f, apply_key_dict)
            if apply_key_dict
            else key: apply_func_on_object_recursively(value, f, apply_key_dict)
            for key, value in obj.items()
        }
    else:
        return f(obj)


async def apply_async_func_on_object_recursively(obj: Any, f: Callable, **kwargs) -> Any:
    if isinstance(obj, list):
        return await gather(
            *[apply_async_func_on_object_recursively(value, f, **kwargs) for value in obj]
        )
    if isinstance(obj, tuple):  # pylint: disable=no-else-return
        return tuple(
            await gather(
                *[apply_async_func_on_object_recursively(value, f, **kwargs) for value in obj]
            )
        )
    elif isinstance(obj, dict):
        keys = [k for k, _ in obj.items()]
        values = await gather(
            *[apply_async_func_on_object_recursively(v, f, **kwargs) for _, v in obj.items()]
        )
        return {key: values[num] for num, key in enumerate(keys)}
    else:
        return await f(obj, **kwargs)
