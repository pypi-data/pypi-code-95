from pathlib import Path
from typing import Any, Iterator, Optional

import miniscule

from apparatus.utils import merge, parents
from apparatus.config.core import Config

Object = Any


def configs(path: Optional[Path] = None) -> Iterator[Object]:
    for parent in parents(path):
        try:
            with open(parent.joinpath(".apparatus.yaml"), "r") as stream:
                obj = miniscule.load_config(stream)
                if obj is not None:
                    yield obj
        except FileNotFoundError:
            pass


def read_config() -> Object:
    acc: Object = {}
    for config in configs():
        acc = merge(acc, config)
    return Config(**acc)


if __name__ == "__main__":
    print(read_config())
