import datetime
import inspect
import logging
import os
import re
import sys


__all__ = [
    'NonOverwriteDict',
    'varname',
    'console_file_logger',
    'load_py_file',
]


class NonOverwriteDict(dict):
    def __setitem__(self, key, value):
        if self.__contains__(key):
            pass
        else:
            dict.__setitem__(self, key, value)


def varname(var):
    """
    https://stackoverflow.com/questions/592746/how-can-you-print-a-variable-name-in-python
    通过调用这个函数时traceback得到code_content，re到需要的var name
    Traceback(filename='<ipython-input-37-5fa84b05d0d4>', lineno=2, function='<module>', code_context=['b = varname(a)\n'], index=0)
    拿到varname(...)里的内容
    """
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
        m = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
    if m:
        return m.group(1)


def console_file_logger(
    logger_name='root',
    log_path=None,
    log_console_level=logging.DEBUG,
    log_file_level=None,
    log_console_format='[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
    log_file_format=None,
    write_init_logs=False,
    reset_handlers=True
):
    """
    TODO: custom init messages
    Setup a logger with name `logger_name` and store in `log_path` if path is defined
    """
    logger = logging.getLogger(logger_name)

    if len(logger.handlers) > 0:
        if reset_handlers:
            for h in logger.handlers:
                logger.removeHandler(h)
        else:
            return logger

    start_time = datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")
    stored_msgs = [
        f'Logger "{logger_name}" created at {start_time}',
        f'Logger "{logger_name}" has level (console): "{log_console_level}"',
        f'Logger "{logger_name}" has format (console): "{log_console_format}"',
    ]

    logger.setLevel(log_console_level)

    formatter = logging.Formatter(log_console_format)

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(log_console_level)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    if log_path is not None:
        file_handler = logging.FileHandler(log_path)

        if log_file_level is None:
            log_file_level = log_console_level
        file_handler.setLevel(log_file_level)

        if log_file_format is None:
            log_file_format = log_console_format
            formatter = logging.Formatter(log_file_format)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stored_msgs.extend([
            f'Set store path of logger {logger_name} to: {log_path}'
            f'Logger "{logger_name}" has level (file): "{log_file_level}"'
            f'Logger "{logger_name}" has format (file): "{log_file_format}"'
        ])

    if write_init_logs:
        for msg in stored_msgs:
            logger.info(msg)

    return logger


def load_py_file(file_path, remove_insert_path='new'):
    """
    :param file_path:

    :param remove_insert_path:
        'any' to remove inserted path even the path is in path list before performing this function
        'new' (default) to remove inserted path from sys path list if this path was not in list before
        False to do nothing
    """
    file_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    file_name_no_suffix = os.path.splitext(os.path.basename(file_name))[0]
    sys.path.insert(-1, file_dir)
    content = {}
    try:
        exec(f'import py file {file_name}', {}, content)
    except ModuleNotFoundError:
        raise FileNotFoundError(f'Not find input file {file_name} with basename {file_name_no_suffix} in {file_dir}')
    return content['content']
