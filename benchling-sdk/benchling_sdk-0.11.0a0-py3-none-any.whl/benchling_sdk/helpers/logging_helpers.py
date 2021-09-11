import logging


def default_logger(name: str = "benchling_sdk") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.addHandler(logging.NullHandler())
    return logger


sdk_logger = default_logger()


def log_deprecation(source_name: str, suggestion: str) -> None:
    sdk_logger.warning(f"{source_name} is deprecated. Please use {suggestion}")
