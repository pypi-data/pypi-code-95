import contextlib
import errno
import os
import sys
from os.path import join as jj
from typing import List

from snakemake.io import expand, glob_wildcards
from snakemake.logging import logger, setup_logger


def expand_basenames(source_folder: str, source_extension: str, years: int = None):
    opts_digits: str = r'\d*'
    any_digits: str = r'\d+'
    year_constraint: str = (
        rf"{{year,{years}\d*}}"
        if isinstance(
            years,
            (int, str),
        )
        else f"{{year,{'|'.join(f'{y}{opts_digits}' for y in years)}}}"
        if isinstance(years, list)
        else rf"{{year,{any_digits}}}"
    )
    source_years, target_basenames = glob_wildcards(jj(source_folder, year_constraint, f"{{file}}.{source_extension}"))
    return source_years, target_basenames


def expand_target_files(
    source_folder: str, source_extension: str, target_folder: str, target_extension: str, years: int = None
) -> List[str]:

    source_years, target_basenames = expand_basenames(source_folder, source_extension, years=years)

    target_files = expand(
        jj(target_folder, "{year}", f"{{basename}}.{target_extension}"),
        zip,
        year=source_years,
        basename=target_basenames,
    )

    return target_files


def setup_logging():

    with contextlib.suppress(Exception):

        if sys.platform == "win32":

            def handler(msg):
                if isinstance(msg, str):
                    print(msg)
                if isinstance(msg, dict):
                    if 'level' in msg and 'debug' in msg['level']:
                        return
                    if 'msg' in msg:
                        print(f"{msg.get('level', '')}: {msg['msg']}")
                        return
                print(msg)

            logger.log_handler = []

            setup_logger(handler=[handler])


WINDOWS_ERROR_INVALID_NAME = 123


def is_valid_path(pathname: str) -> bool:
    """Check if `pathname`is a valid path
    Source: https://stackoverflow.com/questions/9532499/
    """
    try:
        if not isinstance(pathname, str) or not pathname:
            return False
        _, pathname = os.path.splitdrive(pathname)
        root_dir = _root_folder()
        for part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dir + part)
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == WINDOWS_ERROR_INVALID_NAME:  # pylint: disable=no-member
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    except TypeError:
        return False
    else:
        return True


def _root_folder():
    if sys.platform != 'win32':
        return os.path.sep
    return os.environ.get('HOMEDRIVE', 'C:').rstrip(os.path.sep) + os.path.sep
