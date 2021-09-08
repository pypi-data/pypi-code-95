import sys
import logging


def init_logger():
    service_logger = logging.getLogger('fastformers')
    service_logger.propagate = False
    service_logger.setLevel(logging.DEBUG)
    if service_logger.handlers:
        return service_logger

    # create and set formatting for the logging file handler
    fh = logging.StreamHandler(sys.stdout)
    fh.setFormatter(logging.Formatter(fmt="%(asctime)s\t%(message)s", datefmt="%H:%M:%S"))

    # add handler to logger object
    service_logger.addHandler(fh)
    return service_logger


logger = init_logger()
