import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional


class _LoggingState:
    logger_names = []
    log_path = None


def reset_logging(log_path: str, time_stamped: bool = True) -> Optional[str]:
    log_path = Path(log_path)

    for name in _LoggingState.logger_names:
        logger = logging.getLogger(name)
        if isinstance(logger, logging.Logger):
            _remove_logger(logger)

    _LoggingState.logger_names = []
    _LoggingState.log_path = _get_formatted_log_path(log_path, time_stamped)
    return _LoggingState.log_path


def get_logger(name: str) -> logging.Logger:
    if name in _LoggingState.logger_names:
        return logging.getLogger(name)
    raise ValueError(f"logger {name} not yet created")


def create_logger(name: str, sub_path: Optional[str] = None):
    log_path = _get_log_path()
    if sub_path:
        log_path = log_path / sub_path
        log_path.mkdir(parents=True, exist_ok=True)
    return _create_new_logger(name, log_path)


def _create_new_logger(name: str, log_path: Path):
    _LoggingState.logger_names.append(name)
    logger = logging.getLogger(name)
    _add_logger(logger, name, log_path)
    return logger


def _add_logger(logger: logging.Logger, name: str, log_path: Path):
    logger.setLevel(logging.DEBUG)
    ch = _get_handler(log_path, name)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def _get_handler(log_path: Path, name: str):
    log_filename = log_path / (name + ".log")
    return logging.FileHandler(str(log_filename), mode="w")


def _remove_logger(logger: logging.Logger):
    logger.setLevel(logging.NOTSET)
    logger.propagate = True
    logger.disabled = False
    logger.filters.clear()
    handlers = logger.handlers.copy()
    for handler in handlers:
        _remove_handler(logger, handler)


def _remove_handler(logger, handler):
    try:
        handler.acquire()
        handler.flush()
        handler.close()
    except (OSError, ValueError):
        pass
    finally:
        handler.release()
    logger.removeHandler(handler)


def _get_log_path() -> Path:
    if _LoggingState.log_path is None:
        raise ValueError("log_path not set")
    return _LoggingState.log_path


def _get_formatted_log_path(log_path: Optional[Path], time_stamped: bool):
    if log_path is None:
        return

    if time_stamped:
        logtime = datetime.timestamp(datetime.now())
        log_path = log_path / ("logs_" + str(logtime).replace(".", ""))

    log_path.mkdir(parents=True, exist_ok=True)
    return log_path
