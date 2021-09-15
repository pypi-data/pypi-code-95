"""
Created on 2019.08.15
:author: Felix Soubelet

Some utilities for main functionality.
"""
import pathlib
import sys
import time
from contextlib import contextmanager
from typing import Callable, Iterator

from loguru import logger


@contextmanager
def timeit(function: Callable) -> Iterator[None]:
    """
    Returns the time elapsed when executing code in the context via `function`.
    Original code from @jaimecp89

    Args:
        function: any callable taking one argument. Was conceived with a lambda in mind.

    Returns:
        The elapsed time as an argument for the provided function.

    Usage:
        with timeit(lambda spanned: logger.debug(f'Did some stuff in {spanned} seconds')):
            some_stuff()
            some_other_stuff()
    """
    start_time = time.time()
    try:
        yield
    finally:
        time_used = time.time() - start_time
        function(time_used)


def figure_focal_range(focal_length: float) -> str:
    """
    Categorize the focal length value in different ranges. This is better for plotting the
    number of shots per focal length (focal range). To be applied as a lambda on a column
    of your DataFrame.

    Args:
        focal_length: integer or float value of the focal length used for a shot.

    Returns:
        A String for each value, corresponding to the focal range,
    """
    if focal_length <= 0:
        logger.error("Focal length should never be a negative value")
        raise ValueError("Invalid focal length value (< 0)")
    elif focal_length < 16:
        return "1-15mm"
    elif 16 <= focal_length < 23:
        return "16-23mm"
    elif 23 <= focal_length < 70:
        return "24-70mm"
    elif 70 <= focal_length < 200:
        return "70-200mm"
    elif 200 <= focal_length < 400:
        return "200-400mm"
    else:
        return "400mm+"


def set_logger_level(log_level: str = "info") -> None:
    """
    Sets the logger level to the one provided at the commandline.

    Default loguru handler will have DEBUG level and ID 0.
    We need to first remove this default handler and add ours with the wanted level.

    Args:
        log_level: string, the default logging level to print out.

    Returns:
        Nothing, acts in place.
    """
    logger.remove(0)
    logger.add(sys.stderr, level=log_level.upper())


def setup_output_directory(directory_name: str) -> pathlib.Path:
    """
    Create an output directory with the provided name.

    Args:
        directory_name: A string with the name to give to the output directory.

    Returns:
        A `pathlib.Path` object of this directory.
    """
    directory = pathlib.Path(directory_name)
    if not directory.is_dir():
        logger.info(f"Creating output directory {directory.absolute()}")
        directory.mkdir()
    else:
        logger.warning(
            f"Output directory {directory} already present. "
            "This may lead to unexpected behaviour."
        )
    return directory
