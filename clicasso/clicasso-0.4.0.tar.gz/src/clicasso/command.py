from __future__ import annotations

from abc import ABC
from argparse import ArgumentParser
from typing import Union, Tuple

from inflection import dasherize, underscore
from pydantic import BaseModel

from clicasso.connect import connect


Slug = Union[str, Tuple[str, ...]]


def to_slug(name: str) -> Slug:
    return dasherize(underscore(name))


class Command(ABC):
    @classmethod
    def slug(cls) -> Slug:
        return to_slug(cls.__name__)

    @classmethod
    def connect(cls, parser: ArgumentParser) -> None:
        parser.set_defaults(cls=cls)


class BaseCommand(BaseModel, Command):
    @classmethod
    def connect(cls, parser: ArgumentParser) -> None:
        super().connect(parser)
        connect(parser, cls)
