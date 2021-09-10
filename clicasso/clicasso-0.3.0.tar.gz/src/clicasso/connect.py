from typing import Type, Any, Dict
from argparse import ArgumentParser
from pydantic import BaseModel


def connect(parser: ArgumentParser, cls: Type[BaseModel]) -> None:
    for field in cls.__fields__.values():
        kwargs: Dict[str, Any] = {}
        if field.type_ == bool:
            kwargs["action"] = "store_true"
            kwargs["required"] = False
        parser.add_argument(f"--{field.name}", **kwargs)
