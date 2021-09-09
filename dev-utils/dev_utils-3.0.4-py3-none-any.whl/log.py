import os
import logging
from functools import wraps
import datetime
import traceback
from .email_utils import Email


class ErrorFilter(logging.Filter):
    def __init__(self, _email=None):
        super(logging.Filter, self).__init__()
        self._email = _email

    def filter(self, record):
        if record.levelno >= 30:
            msg = record.msg
            file_name = record.filename
            args = record.args
            func_name = args.get("func_name") if isinstance(args, dict) else None
            func_name = record.funcName if func_name is None else func_name
            level_name = record.levelname
            title = "{} LOG (file:{}, func:{}) ".format(level_name, file_name, func_name)
            if self._email:
                self._email.send(title=title, message=msg)
        return True


class Logger:
    def __init__(self):
        self._stream_handler = None
        self._file_handler = None
        self.stream_logger = None
        self.file_logger = None

    def get_stream_logger(self, name, catch_email=None):
        if self._stream_handler is None:
            stream_formatter = logging.Formatter("%(asctime)s   %(module)s   %(levelname)s: %(message)s")
            self._stream_handler = logging.StreamHandler()
            self._stream_handler.setFormatter(stream_formatter)
        _logger = logging.getLogger(name)
        _logger.setLevel(logging.DEBUG)
        _logger.addHandler(self._stream_handler)
        if catch_email:
            _logger.addFilter(filter=ErrorFilter(_email=catch_email))
        return _logger

    def get_file_logger(self, name, path, name_prefix=None, full_name=None, catch_email=None):
        self.mkdir_p(path=path)
        if self._file_handler is None:
            file_formatter = logging.Formatter("%(asctime)s   %(module)s   %(levelname)s: %(message)s")
            if name_prefix:
                file_name = "{}/{}-{}.log".format(path, name_prefix, self.today())
            else:
                file_name = "{}/{}.log".format(path, self.today())
            if full_name:
                file_name = "{}/{}".format(path, full_name)
            self._file_handler = logging.FileHandler(filename=file_name)
            self._file_handler.setFormatter(file_formatter)
        _logger = logging.getLogger(name)
        _logger.setLevel(logging.DEBUG)
        _logger.addHandler(self._file_handler)
        if catch_email:
            _logger.addFilter(filter=ErrorFilter(_email=catch_email))
        return _logger

    @staticmethod
    def log_on_call(_logger: logging.Logger, catch=False):
        def wrapper(func):
            @wraps(func)
            def inner(*args, **kwargs):
                log_info = "[LOG_CALL] {} called.\nargs:\n{}\nkwargs:\n{}".format(func.__name__, args, kwargs)
                _logger.info(log_info)
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    _logger.info("[LOG_CALL] {} raised with exception:".format(func.__name__))
                    _logger.error(traceback.format_exc(), {'func_name': func.__name__})
                    if not catch:
                        raise e
                    else:
                        return None

            return inner

        return wrapper

    @staticmethod
    def mkdir_p(path, is_file_path=False):
        dir_path = os.path.abspath(path)
        if is_file_path:
            dir_path = os.path.dirname(dir_path)
        os.makedirs(dir_path, mode=0o755, exist_ok=True)

    @staticmethod
    def today():
        return str(datetime.datetime.today().date())


if __name__ == '__main__':
    logger = Logger()
    email = Email(user_email="xxxxxx.xxx@xxxxx.cn", password="xxxxxx", email_to="xxxxxx.xxx@xxxxx.cn")
    logger = logger.get_file_logger(name=__name__, path="./", catch_email=email)


    @Logger.log_on_call(_logger=logger)
    def test():
        logger.error("test")


    test()
