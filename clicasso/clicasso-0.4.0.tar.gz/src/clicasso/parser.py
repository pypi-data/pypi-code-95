from __future__ import annotations

import sys
from argparse import ArgumentParser
from typing import List, Optional, Type, Union, Any, Tuple
from dataclasses import dataclass

from pydantic import BaseModel, ValidationError

from clicasso.command import Command, to_slug, Slug
from clicasso.connect import connect
from clicasso.tree import Node


class ParseError(Exception):
    def __init__(self, cause):
        super().__init__(str(cause))
        self.cause = cause


Subparsers = Any


@dataclass
class ParserData:
    parser: ArgumentParser
    subparsers: Optional[Subparsers]

    @classmethod
    def from_parser(cls, parser: ArgumentParser) -> ParserData:
        return cls(parser=parser, subparsers=None)


class CommandParser:
    _root: Node[ParserData]

    def __init__(self, internal: Optional[ArgumentParser] = None):
        self._root = Node(ParserData.from_parser(internal or ArgumentParser()))

    def add(
        self, command: Union[Type[Command], Type[BaseModel]], slug: Optional[Slug] = None
    ) -> None:
        if issubclass(command, Command):
            slug = slug or command.slug()  # type: ignore
            parser = self._get_parser(slug)
            command.connect(parser)  # type: ignore
        elif issubclass(command, BaseModel):
            slug = slug or to_slug(command.__name__)
            parser = self._get_parser(slug)
            parser.set_defaults(cls=command)
            connect(parser, command)

    def _get_parser(self, slug: Slug) -> ArgumentParser:
        def fn(parser_data: ParserData, slug: Slug) -> ParserData:
            if not parser_data.subparsers:
                parser_data.subparsers = parser_data.parser.add_subparsers()
            return ParserData.from_parser(parser_data.subparsers.add_parser(slug[0]))

        if not isinstance(slug, tuple):
            slug = (slug,)
        return self._root.put(slug, fn).value.parser

    def parse(self, args: Optional[List[str]] = None) -> Command:
        (cmd, _) = self.parse_known_args(args)
        return cmd

    def parse_known_args(self, args: Optional[List[str]] = None) -> Tuple[Command, List[str]]:
        parser = self._root.value.parser
        namespace, rest = parser.parse_known_args(args)
        m = vars(namespace)
        try:
            cls = m.pop("cls")
        except KeyError:
            parser.print_usage()
            sys.exit(1)
        try:
            obj = cls(**{k: v for (k, v) in m.items() if v is not None})
            return (obj, rest)  # type: ignore
        except ValidationError as exc:
            raise ParseError(cause=exc) from exc

    @classmethod
    def from_commands(cls, *commands: Type[Command]) -> CommandParser:
        parser = cls()
        for command_cls in commands:
            parser.add(command_cls)
        return parser
