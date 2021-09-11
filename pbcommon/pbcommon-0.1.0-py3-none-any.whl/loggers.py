import logging
from logging.handlers import TimedRotatingFileHandler


def get_logger(
        logger_name,
        logger_file,
        stream_level=None,
        file_level=None
):
    """
    Get a Logger in piggy-bank format
    :param logger_name: Name to give logger
    :param logger_file: File to log to
    :param stream_level: Stream level
    :param file_level: File Level
    :return: Logger
    """
    if file_level is None:
        file_level = logging.DEBUG

    if stream_level is None:
        stream_level = logging.ERROR

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    handler = TimedRotatingFileHandler(logger_file,
                                       when="d",
                                       interval=1)
    handler.setFormatter(formatter)
    handler.setLevel(file_level)

    logger.addHandler(handler)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(stream_level)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(ch)
    logging.basicConfig(level=logging.DEBUG)
    return logger
