import logging
import time

from savvihub.util.constant import VESSL_LOG_LEVEL

LEVEL_MAP = {
    logging.FATAL: "F",  # FATAL is alias of CRITICAL
    logging.ERROR: "E",
    logging.WARN: "W",
    logging.INFO: "I",
    logging.DEBUG: "D",
}


class Formatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        level = LEVEL_MAP.get(record.levelno, "?")

        try:
            formatted_msg = "%s" % (record.msg % record.args)
        except TypeError:
            formatted_msg = record.msg

        record_time = time.localtime(record.created)
        record_message = [
            (
                "%c%02d%02d %02d:%02d:%02d.%06d %s %s:%d] %s"
                % (
                    level,
                    record_time.tm_mon,
                    record_time.tm_mday,
                    record_time.tm_hour,
                    record_time.tm_min,
                    record_time.tm_sec,
                    (record.created - int(record.created)) * 1e6,
                    record.process if record.process is not None else "?????",
                    record.filename,
                    record.lineno,
                    line,
                )
            )
            for line in formatted_msg.split("\n")
        ]
        record_message = "\n".join(record_message)
        record.getMessage = lambda: record_message
        return super().format(record)


def get_logger(level: str = VESSL_LOG_LEVEL):
    logger = logging.getLogger("vessl_logger")
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(Formatter())
    logger.addHandler(handler)
    return logger
