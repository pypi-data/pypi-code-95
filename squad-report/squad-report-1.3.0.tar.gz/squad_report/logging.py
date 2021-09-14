import logging
import os


def getLogger(name=""):
    logger = logging.getLogger(name)
    try:
        log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())
    except AttributeError:
        raise ValueError(f"Invalid log level: '{log_level}'")
    logger.setLevel(log_level)

    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
