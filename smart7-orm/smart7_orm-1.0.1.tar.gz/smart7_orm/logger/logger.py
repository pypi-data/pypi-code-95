import logging
import os
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

# 配置日志颜色
# 通常用于Linux系统下，使控制台输出的日志带颜色
from .. import orm_settings as settings


class ColorFormatter(logging.Formatter):
    log_colors = {
        'CRITICAL': '\033[0;31m',
        'ERROR': '\033[0;33m',
        'WARNING': '\033[0;35m',
        'INFO': '\033[0;32m',
        'DEBUG': '\033[0;00m',
    }

    def format(self, record: logging.LogRecord) -> str:
        s = super().format(record)

        level_name = record.levelname
        if level_name in self.log_colors:
            return self.log_colors[level_name] + s + '\033[0m'
        return s


# 创建日志对象
logger = logging.getLogger('smart7_orm_logger')

logger.setLevel(logging.DEBUG)  # Log等级总开关

# 创建日志目录
log_path = os.getcwd() + '/Logs/'
if not os.path.exists(log_path):
    os.makedirs(log_path)

# 输出到控制台
console_handler = logging.StreamHandler()
# 输出到文件
# file_all_handler = logging.FileHandler(filename=log_path + 'smart7_orm_all.log', mode='a', encoding='utf8')
# file_info_handler = logging.FileHandler(filename=log_path + 'smart7_orm_info.log', mode='a', encoding='utf8')
# file_error_handler = logging.FileHandler(filename=log_path + 'smart7_orm_error.log', mode='a', encoding='utf8')
# 输出到文件,日志切割方式为按日输出
# file_all_handler = TimedRotatingFileHandler(filename=log_path + 'smart7_orm_all.log', when='midnight', encoding='utf8')
# file_info_handler = TimedRotatingFileHandler(filename=log_path + 'smart7_orm_info.log', when='midnight', encoding='utf8')
# file_error_handler = TimedRotatingFileHandler(filename=log_path + 'smart7_orm_error.log', when='midnight', encoding='utf8')
# 输出到文件,日志切割方式为大小输出
file_all_handler = RotatingFileHandler(filename=log_path + 'smart7_orm_all.log', maxBytes=settings.LOG_MAX_SIZE,
                                       backupCount=settings.LOG_BACKUP_COUNT, encoding='utf8')
file_info_handler = RotatingFileHandler(filename=log_path + 'smart7_orm_info.log', maxBytes=settings.LOG_MAX_SIZE,
                                        backupCount=settings.LOG_BACKUP_COUNT, encoding='utf8')
file_error_handler = RotatingFileHandler(filename=log_path + 'smart7_orm_error.log', maxBytes=settings.LOG_MAX_SIZE,
                                         backupCount=settings.LOG_BACKUP_COUNT, encoding='utf8')

# 设置日志级别
console_handler.setLevel(logging.DEBUG)
file_all_handler.setLevel(logging.DEBUG)
file_info_handler.setLevel(logging.INFO)
file_error_handler.setLevel(logging.ERROR)

# 定义handler的输出格式
file_formatter = logging.Formatter(fmt="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
console_formatter = ColorFormatter(fmt="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
console_handler.setFormatter(console_formatter)
file_all_handler.setFormatter(file_formatter)
file_info_handler.setFormatter(file_formatter)
file_error_handler.setFormatter(file_formatter)

# 将logger添加到handler里面
logger.addHandler(console_handler)
logger.addHandler(file_all_handler)
logger.addHandler(file_info_handler)
logger.addHandler(file_error_handler)


def debug(logger_text: str):
    logger.debug(logger_text)


def info(logger_text: str):
    logger.info(logger_text)


def warning(logger_text: str):
    logger.warning(logger_text)


def error(logger_text: str):
    logger.error(logger_text)


def critical(logger_text: str):
    logger.critical(logger_text)
