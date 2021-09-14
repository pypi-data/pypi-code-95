"""
1. Split body line by line
2. Detect Japanese inside each lines
3. Detect line types
    * Header
    * List
    * General
4. Clean up Japanese lines
    * Remove URLs
    * Remove ASCII symbols
5. Detect Paragraphs and wrap by models
"""
from typing import Iterable

from .cleaner import clean_lines
from .lines import parse_lines
from .paragraph import Paragraph, parse_paragraph


def parse(body: str) -> Iterable[Paragraph]:
    lines = parse_lines(body)
    lines = clean_lines(lines)
    return parse_paragraph(lines)
