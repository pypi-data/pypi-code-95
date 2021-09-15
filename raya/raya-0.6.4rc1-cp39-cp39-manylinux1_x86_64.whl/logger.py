from raya.raya import _init_logger as init_logger
from raya.raya import _log as raya_log

init_logger()

class LogLevel:
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    FATAL = 5

def create_logger(name, plain_cout = False):
    def create_logger_wapper(severity, msg):
        if '\n' in msg:
            for m in filter(None, msg.split('\n')):
                raya_log(severity, name, m, plain_cout)    
        else:
            raya_log(severity, name, msg, plain_cout)
    return create_logger_wapper
