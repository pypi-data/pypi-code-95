import logging
import xloil

class WriteLogHandler(logging.Handler):

    def createLock(self):
        self.lock = None

    def acquire(self):
        """
        Acquire the I/O thread lock.
        """
        pass

    def release(self):
        """
        Release the I/O thread lock.
        """
        pass

    def emit(self, record):
        if record.levelno < xloil.log.level:
            return
        msg = self.format(record)

        xloil.log(msg, record.levelno)

