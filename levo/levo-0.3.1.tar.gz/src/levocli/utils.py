import pathlib
import traceback
from typing import List

import requests


def file_exists(path: str) -> bool:
    try:
        return pathlib.Path(path).is_file()
    except OSError:
        # For example, path could be too long
        return False


def fetch_schema_as_lines(schema_source: str) -> List[str]:
    """Fetch the schema file from the source (which can be a file or URL),
    delimited as lines.
    Note: need to add AuthN support later
    """
    schema_spec = []

    if file_exists(schema_source):
        try:
            with open(schema_source) as spec_file:
                schema_spec = spec_file.readlines()
                return schema_spec
        except:
            return schema_spec

    # If we get here, its likely a URL
    try:
        with requests.get(schema_source, stream=True) as spec_page:
            for line in spec_page.iter_lines(decode_unicode=True):
                if line:
                    schema_spec.append(line)
            return schema_spec
    except:
        return schema_spec


def format_exception(error: Exception, include_traceback: bool = False) -> str:
    """Format exception as text."""
    error_type = type(error)
    if include_traceback:
        lines = traceback.format_exception(error_type, error, error.__traceback__)
    else:
        lines = traceback.format_exception_only(error_type, error)
    return "".join(lines)
