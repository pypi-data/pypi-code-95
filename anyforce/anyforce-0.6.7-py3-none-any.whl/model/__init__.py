from typing import Any, Dict

from tortoise import Tortoise

from .base import BaseModel
from .enum import Enum
from .recoverialbe import RecoverableModel


async def init(config: Dict[str, Any]):
    await Tortoise.init(config=config)  # type: ignore


def init_models(config: Dict[str, Any]):
    for name, info in config["apps"].items():
        Tortoise.init_models(info["models"], name)


__all__ = ["Enum", "BaseModel", "RecoverableModel"]
