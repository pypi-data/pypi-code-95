import logging
from fishbase.fish_logger import logger

log_level = ''
log_tag = ''


def log_info(info):
    if logging.INFO == log_level:
        logger.info(log_tag + '{}'.format(info))


def log_warning(warning_info):
    if log_level in [logging.INFO, logging.WARNING]:
        logger.warning(log_tag + '{}'.format(warning_info))


def log_error(error_info):
    if log_level in [logging.INFO, logging.WARNING, logging.ERROR]:
        logger.error(log_tag + '{}'.format(error_info))
