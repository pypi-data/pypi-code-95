import os
import sys
from pathlib import Path
import logging

level_dict = {
    "1": logging.DEBUG,
    "2": logging.INFO,
    "3": logging.WARNING,
    "4": logging.ERROR,
    "5": logging.CRITICAL,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
    }

class LogHandler():

    def __init__(self, file_level="debug", stream_level="info", log_to_file=False, backup_count=10, config=None, config_messages=None):
        self.logger = self._create_or_setup(file_level, stream_level, log_to_file, backup_count, config, config_messages)

    def __enter__(self, file_level="debug", stream_level="info", log_to_file=False, backup_count=10, config=None, config_messages=None):
        return self.logger

    def __exit__(self, et, ev, tb):
        self.close()

    def get_logger(self):
        return self.logger

    def close(self):
        handlers = self.logger.handlers
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)
        logging.shutdown()

    def _create_or_setup(self, file_level="debug", stream_level="info", log_to_file=False, backup_count=10, config=None, config_messages=None):
        if config:
            logger = self.setup_logging(config)
        else:
            logger = self.create_logger(file_level, stream_level, log_to_file, backup_count)
        
        if config_messages:
            for msg in config_messages:
                logging.warning(msg)
            
        return logger

    def setup_logging(self, config):
        from configparser import Error as ConfigError
        from .file_handler import boolean_config_handler
        try:
            return self.create_logger(
                config.get('LOGGING', 'file level'),
                config.get('LOGGING', 'stream level'),
                boolean_config_handler(config, 'LOGGING', 'log to file', default=False),
                backup_count=10
                )
        except ConfigError:
            # Create logger with defaults and log issue
            logging.error("Error retrieving logging levels from config file. Using verbose settings.")
            return self.create_logger()
            

    @staticmethod
    def create_logger(file_level="debug", stream_level="info", log_to_file=False, backup_count=10):
        """
        Creates a logging file handler that creates a new file daily at midnight, with up to 'backup_count' log files saved.
        This also sets logging for stdout to info level.
        
        INPUTS:
        file_level (string or int), stream_level (string or int), backup_count (int)
        
        ACCEPTABLE LOGGING LEVELS:
        debug OR 1
        info OR 2
        warn OR warning OR 3
        error OR 4
        Critical OR 5
        
        Alternatively will default to debug.
        """
        if stream_level in level_dict:
            stream_level = level_dict[stream_level]
        else:
            # use debug if no valid logging level is passed
            stream_level = logging.ERROR
            logging.error("Invalid logging level passed. Stream logging will be set to ERROR")

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_format = logging.Formatter("%(levelname)-8s %(message)s")
        stream_handler.setFormatter(stream_format)

        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)
        stream_handler.setLevel(stream_level)
        logger.addHandler(stream_handler)

        if log_to_file:
            from stitch_m.file_handler import get_user_log_path
            from logging.handlers import TimedRotatingFileHandler
            logpath = get_user_log_path()
            if logpath:
                if file_level in level_dict:
                    file_level = level_dict[file_level]
                else:
                    # use debug if no valid logging level is passed
                    file_level = logging.DEBUG
                    logging.error("Invalid logging level passed. File logging will be set to DEBUG")
                file_handler = TimedRotatingFileHandler(str(logpath / "stitchm_log"), when='midnight', interval=1, backupCount=backup_count)
                file_format = logging.Formatter("%(asctime)s %(levelname)-8s %(filename)s|%(funcName)s: %(message)s", datefmt="%d %b %Y - %H:%M:%S")
                file_handler.setFormatter(file_format)
                file_handler.setLevel(file_level)
                logger.addHandler(file_handler)
        return logger
