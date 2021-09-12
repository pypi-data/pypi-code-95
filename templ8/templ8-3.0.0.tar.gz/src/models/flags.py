from dataclasses import dataclass
from typing import Type, TypeVar

from ..models.cli import CLI
from ..utils.parsers.dataclasses import pick_into_dataclass

T = TypeVar("T", bound="Flags")  # pylint: disable = C0103


@dataclass
class Flags:
    loglevel: int
    dry_run: bool

    @classmethod
    def parse(cls: Type[T], cli: CLI) -> T:
        return pick_into_dataclass(cls, cli, {"loglevel": cli.loglevel})
