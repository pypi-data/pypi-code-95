"""
utilities shared by bdrc_utils
"""
import argparse
from pathlib import Path
from typing import AnyStr


def reallypath(what_path: AnyStr) -> Path:
    """
    Resolves everything about the path
    :param what_path: Pathlike object
    :return: fully resolved path
    """
    from os import path

    return path.realpath(path.expandvars(path.expanduser(what_path))) if what_path is not None else None

