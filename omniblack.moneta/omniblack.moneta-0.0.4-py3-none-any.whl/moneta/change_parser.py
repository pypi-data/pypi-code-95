from enum import Enum
from dataclasses import dataclass, field
from .yaml import yaml
from ruamel.yaml import yaml_object


str_tag = 'tag:yaml.org,2002:str'


@yaml_object(yaml)
class Severity(Enum):
    none = 'none'
    patch = 'patch'
    minor = 'minor'
    major = 'major'

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(str_tag, node.value)


@dataclass
class ChangeInfo:
    name: str
    severity: Severity
    message: list[str] = field(default_factory=list)


indent_chars = {'\u0020', '\u0009'}  # Space and tab


def get_indent(line):
    indent = ''
    if line[0] in indent_chars:
        for char in line:
            if char in indent_chars:
                if char != line[0]:
                    raise ValueError('Mixed indent is not allowed.')
                else:
                    indent += char
            else:
                return indent


def has_indent(line, indent):
    return line.startswith(indent)


stop = 'stop'


async def parse(file):
    changes = [
        change
        async for change in Parser(file)
        if change.severity is not Severity.none
    ]

    return changes


class Parser:
    def __init__(self, file):
        self.lines = file.__aiter__()
        self.__line = None
        self.__line_num = None

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.__line is None:
            await self.next_line()

        if self.__line is stop:
            raise StopAsyncIteration()

        return await self.package_change()

    async def package_change(self):
        line = self.__line

        while not self.__stripped_line:
            await self.next_line()
            line = self.__line

        if line[0] in indent_chars:
            self.raise_syntax('Unexpected indent')

        split = line.split(':')

        if len(split) != 2:
            self.raise_syntax('Line does not match package change format')

        severity, pkg = split
        pkg = pkg.strip()
        severity = Severity(severity.strip().lower())

        try:
            await self.next_line()
        except StopAsyncIteration:
            return ChangeInfo(pkg, severity)

        message = await self.message()

        return ChangeInfo(pkg, severity, message)

    async def next_line(self):
        if self.__line_num is None:
            self.__line_num = 0
        else:
            self.__line_num += 1

        try:
            new_line = await self.lines.__anext__()
        except StopAsyncIteration:
            self.__line = stop
            raise
        else:
            if new_line.startswith('%'):
                return await self.next_line()
            self.__line = new_line
            self.__stripped_line = new_line.strip()

    def raise_syntax(self, message):
        raise SyntaxError(
            message,
            (
                'Severity Question',
                self.__line_num,
                0,
                self.__line,
            ),
        )

    async def message(self):
        while not self.__stripped_line:
            try:
                await self.next_line()
            except StopAsyncIteration:
                return []

        indent = get_indent(self.__line)

        if indent is None:
            return []

        message = [self.__line.removeprefix(indent)]
        empty_lines = []
        try:
            await self.next_line()
        except StopAsyncIteration:
            return message

        while has_indent(self.__line, indent) or not self.__stripped_line:
            if not self.__stripped_line:
                empty_lines.append(self.__line)
                try:
                    await self.next_line()
                except StopAsyncIteration:
                    return message
            else:
                if empty_lines:
                    message.extend(empty_lines)
                    empty_lines = []

                message.append(self.__line.removeprefix(indent))
                try:
                    await self.next_line()
                except StopAsyncIteration:
                    return message

        return message
