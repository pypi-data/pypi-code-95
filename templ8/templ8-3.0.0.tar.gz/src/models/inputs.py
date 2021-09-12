from dataclasses import dataclass
from typing import Type, TypeVar

from ..models.cli import CLI
from ..models.flags import Flags
from ..models.settings import Settings

T = TypeVar("T", bound="Inputs")  # pylint: disable = C0103


@dataclass
class Inputs:
    flags: Flags
    settings: Settings

    @classmethod
    def parse(cls: Type[T], cli: CLI) -> T:
        return cls(Flags.parse(cli), Settings.parse(cli))
