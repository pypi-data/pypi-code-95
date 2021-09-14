import logging
import os
from logging.handlers import TimedRotatingFileHandler

import json_logging

from aide_sdk.logger.appender import JsonAppender


default_log_level = logging.getLevelName(os.environ.get('AIDE_LOG_LEVEL', 'INFO'))


class LogManager:
    logger = None
    audit_logger = None
    stream_handler = logging.StreamHandler()
    audit_file_handler = TimedRotatingFileHandler('aide-audit.log', when='midnight')
    file_handler = TimedRotatingFileHandler('aide.log', when='midnight')

    @staticmethod
    def get_logger(log_level=None):
        if LogManager.logger is None:
            LogManager.logger = LogManager._create_logger(
                "aide-logger",
                log_level=log_level,
                file_handler=LogManager.file_handler)
        return LogManager.logger

    @staticmethod
    def _get_audit_logger(log_level=None):
        if LogManager.audit_logger is None:
            LogManager.audit_logger = LogManager._create_logger(
                "aide-audit-logger",
                log_level=log_level,
                file_handler=LogManager.audit_file_handler)
        return LogManager.audit_logger

    @staticmethod
    def _create_logger(logger_name, log_level, file_handler):
        logger = logging.getLogger(logger_name)
        logger.propagate = False
        logger.setLevel(log_level or default_log_level)
        logger.handlers = [LogManager.stream_handler, file_handler]
        return logger

    @classmethod
    def init_logging(cls, log_level=None):
        json_logging.init_non_web(enable_json=True, custom_formatter=JsonAppender)
        logging.basicConfig(handlers=[cls.stream_handler, cls.file_handler],
                            level=log_level or default_log_level)
        json_logging.config_root_logger()
