import sys
import inspect

DISABLE_SYS_EXIT = False

class NoTraceBackWithLineNumber(Exception):
    def __init__(self, msg):
        try:
            ln = sys.exc_info()[-1].tb_lineno
        except AttributeError:
            ln = inspect.currentframe().f_back.f_lineno
        self.args = "{0.__name__}: {1}".format(type(self), msg),

        if not DISABLE_SYS_EXIT:
            sys.exit(self)

class CnvrgError(NoTraceBackWithLineNumber):
    pass

class UserError(CnvrgError):
    pass

class NotImplementedError(CnvrgError):
    pass

class UnknownStsError(CnvrgError):
    pass

class APINotFound(Exception):
    pass