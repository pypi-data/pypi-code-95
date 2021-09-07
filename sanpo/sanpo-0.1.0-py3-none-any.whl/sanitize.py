# Copyright (c) 2021, Thomas Aglassinger
# All rights reserved. Distributed under the BSD 3-Clause License.
import logging
import re

_LINE_PATTERNS_TO_REMOVE = [
    re.compile(line)
    for line in [
        r'"Project-Id-Version: PACKAGE VERSION\\n"',
        r'"Report-Msgid-Bugs-To: \\n"',
        r'"POT-Creation-Date: .+\\n"',
        r'"PO-Revision-Date: .+\\n"',
        r'"Last-Translator: FULL NAME EMAIL@ADDRESS\\n"',
        r'"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"',
        r'"Language-Team: LANGUAGE LL@li.org\\n"',
        r'"Language-Team: LANGUAGE <LL@li.org>\\n"',
    ]
]

_log = logging.getLogger("sanpo")


def sanitize_file(po_path: str):
    _log.info("sanitizing %s", po_path)
    with open(po_path, encoding="utf-8") as po_file:
        lines_to_write = list(sanitize_lines(po_file))
    with open(po_path, "w", encoding="utf-8") as po_file:
        for line_to_write in lines_to_write:
            po_file.write(line_to_write)


def sanitize_lines(source_lines):
    for line in source_lines:
        line_has_to_be_removed = any(
            line_pattern_to_remove.match(line) for line_pattern_to_remove in _LINE_PATTERNS_TO_REMOVE
        )
        if not line_has_to_be_removed:
            yield line
