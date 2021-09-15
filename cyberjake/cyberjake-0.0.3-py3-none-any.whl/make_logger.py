"""Common log maker"""
import logging


def make_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """Creates a logger class that handles stream and file output

    :param name: Name of logger
    :type name: str
    :param log_level: Logging level. Valid strings are 'DEBUG', 'INFO', 'WARNING',
            'ERROR', 'CRITICAL'
    :type log_level: str
    :return: Logger class that handled the logging.
    :rtype: logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    formatter = logging.Formatter(
        "%(levelname)s - %(name)s - %(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    file_output = logging.FileHandler("{}.log".format(name), mode="w")
    file_output.setFormatter(formatter)
    logger.addHandler(file_output)
    stream_output = logging.StreamHandler()
    stream_output.setFormatter(formatter)
    logger.addHandler(stream_output)
    return logger
