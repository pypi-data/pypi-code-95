"""
loggin utilities
"""
import typing
from contextlib import contextmanager
import logging
import time


def progressbar(
    iterable: typing.Iterable, logger: typing.Optional[logging.Logger] = None
):
    """
    Args:
        iterable
        logger: optional

    Examples:
        >>> import logging
        >>> import rna
        >>> import sys
        >>> sys.modules['tqdm'] = None
        >>> log = logging.getLogger(__name__)

        >>> a = range(3)
        >>> for value in rna.log.progressbar(a, logger=log):
        ...     _ = value * 3

    """
    if logger is None:
        logger = logging
    try:
        # tqdm not required for the module to work
        from tqdm import tqdm as progressor  # pylint: disable=import-outside-toplevel

        tqdm_exists = True
    except ImportError:

        def progressor(iterable):
            """
            dummy function. Does nothing
            """
            return iterable

        tqdm_exists = False
    try:
        n_total = len(iterable)
    except TypeError:
        n_total = None

    for i in progressor(iterable):
        if not tqdm_exists:
            if n_total is None:
                logger.info("Progress: item {i}".format(**locals()))
            else:
                logger.info("Progress: {i} / {n_total}".format(**locals()))
        yield i


@contextmanager
def timeit(
    process_name: str = "No Description",
    *args,
    logger: typing.Optional[logging.Logger] = None,
    precision=1,
) -> None:
    """
    Context manager for autmated timeing

    Args:
        process_name (str): message to customize the log message
        logger
        precision (int): show until 10^-<precision> digits

    Examples:
        >>> import rna
        >>> with rna.log.timeit("Logger Name"):
        ...     # Some very long calculation
        ...     pass
    """
    if logger is None:
        logger = logging
    start_time = time.time()
    logger.log(logging.INFO, "Timing Process: " + process_name + " ...", *args)

    yield

    logger.log(
        logging.INFO,
        "\t\t\t\t\t\t... Process Duration: %1." + str(int(precision)) + "f s",
        time.time() - start_time,
    )
