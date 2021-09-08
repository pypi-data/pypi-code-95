"""Logging logger and handler via the neobulkmp cache backend
    """
import logging
import threading
from .cache_backend import CacheInterface

# Logger class on worker processes side. This serializes the log records and write them into the cache backend


class CacheLoggerHandler(logging.Handler):  # inherit from Handler class
    def __init__(self, cache: CacheInterface):
        logging.Handler.__init__(self)  # run parent __init__ class
        self.cache = cache

    def emit(self, record: logging.LogRecord):
        # Write log into caching backend
        self.cache.write_log(record)


def _handle_log_records(cache):
    for record in cache.fetch_logs():
        logger = logging.getLogger(record.name)
        logger.handle(record)


# Logger class on main process side. This grabs the serialized log records from the cache backend and logs them on the main process side


class LogRecordStreamHandler:
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    def __init__(self, cache):
        self.cache = cache

    def handle(self):
        # _thread.start_new_thread(_test, ())
        # Todo: I dont know why the threading function does not work as local class method?
        # Did the same in https://git.connect.dzd-ev.de/dzdpythonmodules/ptan/-/blob/master/ptan/server.py#L159
        # for now we just outsource it to a standalone func '_handle_log_records'
        self.log_thread = threading.Thread(
            target=_handle_log_records, args=(self.cache,)
        )
        self.log_thread.daemon = True
        self.log_thread.start()

    def handleLogRecord(self, record: logging.LogRecord):
        logger = logging.getLogger(record.name)
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and bandwidth!
        logger.handle(record)
