import logging
import re
from functools import reduce
from typing import Any, Dict

from jinja2schema import infer, to_json_schema

from ..services.templates import pipes

logger = logging.getLogger(__file__)


custom_tokens = [
    r"{% include .* %}",
    *[rf"(\| ?)?{i}(\(.*\))?" for i in pipes],
]


def schema(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf8") as stream:
        return to_json_schema(
            infer(
                reduce(
                    lambda acc, x: re.sub(x, "", acc),
                    custom_tokens,
                    stream.read(),
                )
            )
        )
