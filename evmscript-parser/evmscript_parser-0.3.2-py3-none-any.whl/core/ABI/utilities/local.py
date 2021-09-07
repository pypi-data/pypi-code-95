"""
Utilities for work with local interfaces.
"""
import os
import json
import glob

from typing import Dict, Optional

from evmscript_parser.core.ABI.storage import ABI_T

_NameT = str
_PathT = str


def get_all_files(
        directory_path: str,
        search_pattern: Optional[str] = None
) -> Dict[_NameT, _PathT]:
    """Get all files from directory."""
    if search_pattern is None:
        search_pattern = '*'

    return {
        os.path.basename(path): path
        for path in glob.glob(os.path.join(
            directory_path, search_pattern
        ))
    }


def read_abi_from_json(json_path: str) -> ABI_T:
    """Read ABI from json file."""
    with open(json_path, 'r') as f:
        return json.load(f)
