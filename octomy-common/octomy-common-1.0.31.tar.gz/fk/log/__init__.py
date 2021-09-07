import logging
import sys
import os
import inspect
import warnings

log_setup_once = False


def setup_logging(name=None, log_level=logging.INFO):
    """Set up logging."""
    global log_setup_once
    if not log_setup_once:
        log_setup_once = True
        logging.basicConfig(level=log_level)
        fmt = "%(asctime)s %(levelname)s (%(threadName)s) [%(name)s:%(lineno)s::%(funcName)s()] - %(message)s"
        colorfmt = "%(log_color)s{}%(reset)s".format(fmt)
        datefmt = "%Y-%m-%d %H:%M:%S"

        # Suppress overly verbose output that isn't helpful from some libraries we depend on
        for key in ["requests", "tensorboard", "urllib3", "aiohttp.access", "uamqp", "sqlalchemy", "sqlalchemy.engine.base", "matplotlib.font_manager"]:
            logging.getLogger(key).setLevel(logging.WARNING)

        # Enable debug logging for some insteresting libraries (for development)
        logging.getLogger("fk").setLevel(logging.DEBUG)

        try:
            from colorlog import ColoredFormatter

            logging.getLogger().handlers[0].setFormatter(ColoredFormatter(colorfmt, datefmt=datefmt, reset=True, log_colors={"DEBUG": "cyan", "INFO": "green", "WARNING": "yellow", "ERROR": "red", "CRITICAL": "red"}))
        except ImportError:
            # Ignore failures in loading color coded logs
            pass

        # Set this log level as default
        logger = logging.getLogger("")
        logger.setLevel(log_level)
    if not name:
        name = inspect.stack()[1][1]
    logger = logging.getLogger(name)
    try:
        import colored_traceback.auto
    except ImportError:
        pass

    return logger
