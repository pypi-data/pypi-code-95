import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Union


def read_file(file: str) -> str:
    """
    Reads a file.

    Args:
        file (str): file to read

    Returns:
        (str): content
    """
    content = ""
    with open(file) as fp:
        content = fp.read()
    return content


def read_lines(file: str) -> List[str]:
    """
    Reads lines from a file.

    Args:
        file (str): file to read

    Returns:
        (List[str]): lines of content
    """
    content = []
    with open(file) as fp:
        content = fp.readlines()
    return content


def check_file_exists(file: str) -> bool:
    """
    Checks if a file exists

    Args:
        file (str): file to check

    Returns:
        (bool): whether the file exists or not
    """
    return Path(file).is_file()


def move_file(filepath: str, new_path: str) -> None:
    """
    Moves a file.

    Args:
        filepath (str): file to move
        new_path (str): new location
    """
    os.rename(filepath, new_path)


def save_file(
    filepath: str, data: Union[str, Dict], is_json: Optional[bool] = False
) -> None:
    """
    Saves a file.

    Args:
        filepath (str): file to move
        data (str): data to write to file
    """
    if is_json:
        with open(filepath, "w") as fp:
            json.dump(data, fp, indent=2)
        return

    with open(filepath, "w") as fp:
        fp.write(data)
