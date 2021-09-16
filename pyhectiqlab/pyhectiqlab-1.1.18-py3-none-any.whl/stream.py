import logging

class LogHandler(logging.StreamHandler):
    """
    A handler class which allows the cursor to stay on
    one line for selected messages
    """
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            _msg = msg
            if len(msg)<2 or msg[-1:]!="\r":
                _msg += self.terminator
            stream.write(_msg)
            self.callback(_msg)
            # Write logs on the server right here.
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
