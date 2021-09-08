import logging
import sys
import types
import logging.config


def setup_logger(level=logging.INFO, config=None, stdout=True):
    """
    There are mainly two practical forms of calling this:

    1- setup_logger()
    Used normally in an earlier stage when the sc_pack_config is not loaded.
    With this, only the console logging handler
    gets used.

    2- setup_logger(config=config)
    Used after you load the a specific config. We use the following info:

    Can be called multiple times.
    """
    if logging.root.handlers:
        logging.root.setLevel(level)
        if config is not None:
            for handler in logging.root.handlers:
                if hasattr(handler, "setConfig"):
                    handler.setConfig(config)
    else:
        dictConfig = {
            "version": 1,
            "formatters": {
                "stdout": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler" if stdout else "logging.NullHandler",
                    "formatter": "stdout",
                    "level": logging.DEBUG
                },
            },
            "loggers": {
                "toilmoresdk": {"propagate": True},
            },
            "root": {
                "handlers": ["stdout"],
                "level": level,
            }
        }
        try:
            logging.config.dictConfig(dictConfig)
        except Exception:
            logging.exception(
                "toilmoresdk setting-up the full-feature logging fails"
            )

    if isinstance(sys.excepthook, types.BuiltinFunctionType):
        sys.excepthook = _make_excepthook(sys.excepthook)


def _make_excepthook(old_excepthook):
    def logger_excepthook(exc_type, exc_value, exc_traceback):
        logging.error(
            "Uncaught exception occurred!",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        return old_excepthook(exc_type, exc_value, exc_traceback)
    return logger_excepthook
