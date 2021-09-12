import logging


LOG_LEVEL = logging.DEBUG


def _get_console_handler():
    handler = logging.StreamHandler()
    handler.setLevel(LOG_LEVEL)
    handler.setFormatter(logging.Formatter(
        """
%(levelname)s | %(asctime)s | pid: %(process)d | %(pathname)s:%(lineno)s #%(funcName)s
%(message)s"""
    ))
    return handler


def get_logger():
    """

    Returns:
        logging.Logger
    """
    logger = logging.getLogger('ds-toolkit')

    if not len(logger.handlers):
        logger.setLevel(logging.DEBUG)
        logger.addHandler(_get_console_handler())

    return logger
