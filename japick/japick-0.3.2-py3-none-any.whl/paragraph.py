from dataclasses import dataclass
from typing import Iterable, List, Optional

from .lines import Line
from .syntax import NULL_SYMBOL


@dataclass
class Pos:
    """Line number and column position.
    These numbers starts from Zero.
    """

    line: int
    ch: int

    def __eq__(self, other) -> bool:
        return self.line == other.line and self.ch == other.ch

    def __repr__(self) -> str:
        return f"Pos({self.line}, {self.ch})"


@dataclass
class Paragraph:
    number: int
    index: int
    lines: List[str]
    is_head: bool = False
    is_list: bool = False
    _body: Optional[str] = None

    def __eq__(self, other):
        return (
            self.number == other.number
            and self.index == other.index
            and self.lines == other.lines
            and self.is_head is other.is_head
            and self.is_list is other.is_list
        )

    @property
    def body(self):
        if self._body is not None:
            return self._body
        self._body = "\n".join(line.strip().replace(NULL_SYMBOL, "") for line in self.lines)
        return self._body

    def as_original_pos(self, index) -> Pos:
        before_lines = self.body[:index].split("\n")
        pos = Pos(
            len(before_lines) - 1,
            len(before_lines[-1]),
        )
        # Convert column number to original position.
        line = self.lines[pos.line]
        left_margin = len(line) - len(line.lstrip())
        chunks = line[left_margin:].split(NULL_SYMBOL)
        num_null_symbols = 0
        current = 0
        for num_null_symbols, chunk in enumerate(chunks):
            current += len(chunk)
            if pos.ch < current:
                break
        pos.line += self.number
        pos.ch += left_margin + num_null_symbols
        return pos

    def as_original_index(self, index: int) -> int:
        pos = self.as_original_pos(index)
        num_lines = pos.line - self.number
        before_index = sum(len(line) for line in self.lines[:num_lines]) + num_lines
        return self.index + before_index + pos.ch

    def __str__(self) -> str:
        return self.body

    def __repr__(self) -> str:
        body = self.body
        if self.is_head:
            body = "# " + body
        elif self.is_list:
            body = "* " + body
        return f"Paragraph({self.number}. ({self.index}) {body})"

    def append(self, line: str):
        self.lines.append(line)

    def __bool__(self) -> bool:
        return bool(self.lines)


def parse_paragraph(lines: Iterable[Line]) -> Iterable[Paragraph]:
    """
    Combine multiple lines into one Paragraph.
    Each paragraphs has chunks.
    """
    paragraph = Paragraph(0, 0, [])
    index = 0
    for i, line in enumerate(lines):
        next_index = index + len(line.body) + 1

        if line.is_ignore or line.is_head or line.is_list:
            if paragraph:
                yield paragraph
            paragraph = Paragraph(i + 1, next_index, [])

        if line.is_head or line.is_list:
            # Yield my self as 1 line paragraph.
            yield Paragraph(
                i,
                index,
                [line.body],
                is_head=line.is_head,
                is_list=line.is_list,
            )
        elif not line.is_ignore:
            paragraph.append(line.body)

        index = next_index

    if paragraph:
        yield paragraph
