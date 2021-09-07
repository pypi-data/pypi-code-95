from threading import Timer
import logging

logger = logging.getLogger(__name__)


class Watchdog(BaseException):
    def __init__(self, timeout, userHandler=None):  # timeout in seconds
        self.timeout = timeout
        # logger.info(f"WATCHDOG SET WITH TIME {self.timeout}")
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()

    def reset(self):
        self.timer.cancel()
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()

    def stop(self):
        # logger.info(f"WATCHDOG STOPPED")
        self.timer.cancel()

    def defaultHandler(self):
        logger.info("WATCHDOG TIMED OUT")
        raise self
