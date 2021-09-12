import logging
import os
from typing import Any, Dict, List

from convert_case import (camel_case, is_camel_case, is_kebab_case,
                          is_pascal_case, is_sentence_case, is_snake_case,
                          is_title_case, is_upper_case, kebab_case,
                          pascal_case, sentence_case, snake_case, title_case,
                          upper_case)
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ..models.timestamps import Timestamp
from ..utils.collections.dicts import merge_dicts
from ..utils.strings.paths import path_head, path_tail
from ..utils.strings.pipes import (handle, pad_in, pluralize, quote,
                                   remove_prefix, without_ends, without_first,
                                   without_last)

logger = logging.getLogger(__file__)


pipes = {
    "camel_case": camel_case,
    "handle": handle,
    "is_camel_case": is_camel_case,
    "is_kebab_case": is_kebab_case,
    "is_pascal_case": is_pascal_case,
    "is_sentence_case": is_sentence_case,
    "is_snake_case": is_snake_case,
    "is_title_case": is_title_case,
    "is_upper_case": is_upper_case,
    "kebab_case": kebab_case,
    "pad_in": pad_in,
    "pascal_case": pascal_case,
    "pluralize": pluralize,
    "quote": quote,
    "remove_prefix": remove_prefix,
    "sentence_case": sentence_case,
    "snake_case": snake_case,
    "title_case": title_case,
    "upper_case": upper_case,
    "without_ends": without_ends,
    "without_first": without_first,
    "without_last": without_last,
}


def parse_template(
    path: str, loader_paths: List[str], render_context: Dict[str, Any]
) -> str:
    loader_paths = [
        os.getcwd(),
        *loader_paths,
        path_tail(path),
    ]

    env = Environment(
        loader=FileSystemLoader(loader_paths),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=True,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )

    env.filters = merge_dicts(env.filters, pipes, Timestamp.now().__dict__)

    return env.get_template(path_head(path)).render(**render_context)
