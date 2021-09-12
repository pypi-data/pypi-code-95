import sys
from inspect import Parameter, signature
from typing import Any, Dict, List, Optional, Type, TypeVar

from ...utils.collections.dicts import merge_dicts, without
from ...utils.parsers.exceptions import MissingDataclassArguments

T = TypeVar("T")  # pylint: disable = C0103


def dataclass_keys(cls: Any) -> List[str]:
    return list(signature(cls.__init__).parameters.keys())


def annotation_default(parameter: Parameter) -> Any:
    if str(parameter.default) != "<factory>":
        return parameter.default

    if sys.version_info > (3, 7, 0):
        factory_key = "__origin__"

    elif sys.version_info > (3, 6, 0):
        factory_key = "__extra__"

    else:
        raise NotImplementedError

    getter = getattr(parameter.annotation, factory_key)

    return getter()


def dataclass_defaults(cls: Any) -> Dict[str, Any]:
    return {
        k: annotation_default(v)
        for k, v in without(dict(signature(cls.__init__).parameters), "self").items()
        if v.default != Parameter.empty
    }


def dataclass_required(cls: Any) -> List[str]:
    return [
        k
        for k, v in without(dict(signature(cls.__init__).parameters), "self").items()
        if v.default == Parameter.empty
    ]


def parse_dataclass_kwargs(cls: Type[T], kwargs: Dict[str, Any]) -> T:
    missing = set(dataclass_required(cls)) - set(kwargs.keys())

    if missing:
        raise MissingDataclassArguments(missing)

    return cls(**kwargs)  # type: ignore


def filter_into_dataclass(
    cls: Type[T], dct: Dict[str, Any], overrides: Optional[Dict[str, Any]] = None
) -> T:
    return parse_dataclass_kwargs(
        cls,
        merge_dicts(
            {k: v for k, v in dct.items() if k in dataclass_keys(cls)},
            overrides if overrides is not None else {},
        ),
    )


def pick_into_dataclass(
    cls: Type[T], obj: Any, overrides: Optional[Dict[str, Any]] = None
) -> T:
    return parse_dataclass_kwargs(
        cls,
        merge_dicts(
            {i: getattr(obj, i) for i in dataclass_keys(cls) if hasattr(obj, i)},
            overrides if overrides is not None else {},
        ),
    )
