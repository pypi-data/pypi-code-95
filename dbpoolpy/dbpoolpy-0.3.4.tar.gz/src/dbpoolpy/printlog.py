def print_dec(func):
    def _(cls, *msg):
        for m in msg:
            print(m)
    return _

class PrintLog:
    
    @classmethod
    @print_dec('info')
    def info(cls, *msg):
        pass

    @classmethod
    @print_dec('error')
    def error(cls, *msg):
        pass

    @classmethod
    @print_dec('warning')
    def warning(cls, *msg):
        pass

    @classmethod
    @print_dec('warn')
    def warn(cls, *msg):
        pass

    @classmethod
    @print_dec('debug')
    def debug(cls, *msg):
        pass

