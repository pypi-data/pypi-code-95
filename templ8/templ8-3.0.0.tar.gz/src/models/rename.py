from dataclasses import dataclass
from typing import Dict, Type, TypeVar, Union

from ..models.exceptions import InvalidRename

T = TypeVar("T", bound="Rename")  # pylint: disable = C0103


@dataclass
class Rename:
    segment: str
    token: str

    @classmethod
    def parse(cls: Type[T], obj: Union[str, Dict[str, str]]) -> T:
        if isinstance(obj, str):
            return cls(segment=obj, token=obj)

        if not isinstance(obj, dict) or "segment" not in obj:
            raise InvalidRename(obj)

        return cls(obj["segment"], obj["token"] if "token" in obj else obj["segment"])
