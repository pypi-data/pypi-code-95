from dataclasses import dataclass, field
from typing import Any, Dict, List, Type, TypeVar

from ..models.initialization import Initialization
from ..models.rename import Rename
from ..utils.collections.dicts import merge_dicts
from ..utils.parsers.dataclasses import filter_into_dataclass
from ..utils.parsers.files import parse_json

T = TypeVar("T", bound="Collection")  # pylint: disable = C0103


@dataclass
class Collection:
    name: str
    root: str

    default_variables: Dict[str, Any] = field(default_factory=dict)

    renames: List[Rename] = field(default_factory=list)
    initializations: List[Initialization] = field(default_factory=list)

    @classmethod
    def parse(cls: Type[T], path: str) -> T:
        raw = merge_dicts({"root": path}, parse_json(path))

        if "initializations" in raw:
            raw["initializations"] = [
                Initialization.parse(i) for i in raw["initializations"]
            ]

        if "renames" in raw:
            raw["renames"] = [Rename.parse(i) for i in raw["renames"]]

        return filter_into_dataclass(cls, raw)
