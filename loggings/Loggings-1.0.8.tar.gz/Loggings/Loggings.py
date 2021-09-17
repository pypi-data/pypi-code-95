# -- coding:UTF-8 –

import time
from loguru import logger
from pathlib import Path

project_path = Path.cwd().parent
log_path = Path(project_path, "log")
t = time.strftime("%Y_%m_%d")

class Loggings:
    __instance = None
    logger.add(f"{log_path}/interface_log_{t}.log", rotation="500MB", encoding="utf-8", enqueue=True, retention="10 days")
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Loggings, cls).__new__(cls, *args, **kwargs)

        return cls.__instance

    def info(self, msg):
        return logger.info("\033[32m{}\033[0m".format(msg))

    def debug(self, msg):
        return logger.debug("\033[34m{}\033[0m".format(msg))

    def warning(self, msg):
        return logger.warning("\033[33m{}\033[0m".format(msg))

    def error(self, msg):
        return logger.error("\033[31m{}\033[0m".format(msg))

    def success(self, msg):
        return logger.success("\033[32m{}\033[0m".format(msg))


# loggings = Loggings1()
# if __name__ == '__main__':
#     loggings.info("中文test")
#     loggings.debug("中文test")
#     loggings.warning("中文test")
#     loggings.error("中文test")
#     loggings.success("中文test")
#
#     Loggings1.info('If you are using Python {}, prefer {feature} of course!', 3.6, feature='f-strings')
#     n1 = "cool"
#     n2 = [1, 2, 3]
#     Loggings1.info(f'If you are using Python {n1}, prefer {n2} of course!')

