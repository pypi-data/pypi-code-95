from typing import Callable

from .syntax import (
    CODE_REGEX,
    HEAD_REGEX,
    HTML_REGEX,
    LINK_REGEX,
    LIST_REGEX,
    MASK_SYMBOL,
    NULL_SYMBOL,
    QUOTE_REGEX,
    SYMBOL_REGEX,
    URL_REGEX,
)


def fill(symbol: str) -> Callable:
    def _runner(matched) -> str:
        return symbol * len(matched[0])

    return _runner


def clean(line):
    """
    * Remove URL
    * Remove Markdown symbols and fill by spaces.
        * List * - 1. * [ ] ...
        * Quote > ...
        * Heading # ...
        * Link and Image [...]()
        * Bold * _
        * Strikethrough ~
    * Mask texts inside Codes `...`
    """
    line.body = LIST_REGEX.sub(fill(" "), line.body)
    line.body = QUOTE_REGEX.sub(fill(" "), line.body)
    line.body = HEAD_REGEX.sub(fill(" "), line.body)
    line.body = LINK_REGEX.sub(
        lambda m: NULL_SYMBOL * len(m[1]) + m[2] + NULL_SYMBOL * len(m[3]), line.body
    )
    line.body = HTML_REGEX.sub(fill(NULL_SYMBOL), line.body)
    line.body = URL_REGEX.sub(fill(NULL_SYMBOL), line.body)
    line.body = SYMBOL_REGEX.sub(fill(NULL_SYMBOL), line.body)
    line.body = CODE_REGEX.sub(fill(MASK_SYMBOL), line.body)
    return line


def clean_lines(lines):
    for line in lines:
        if not line.is_ignore:
            clean(line)
        yield line
