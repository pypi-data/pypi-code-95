# -*- coding: utf-8 -*-
# @Time    : 2021/9/9 19:54
# @Author  : chinablue
# @Email   : dongjun@reconova.cn
# @File    : log.py

import logging
from io import StringIO


# 日志开关: verbose
class Logger():

    def __init__(self, verbose=None, capture_console=None):
        """

        :param verbose:
        :param capture_console:
        >>> logger = Logger(verbose=True, capture_console=False)
        >>> logger.info("info")
        >>> logger.error("error")
        >>> logger.close()
        2021-09-10 15:45:00,446.446 [INFO] root info : info
        2021-09-10 15:45:00,446.446 [ERROR] root error : error


        """

        if verbose is None:
            verbose = True

        if capture_console is None:
            capture_console = False

        self.close()

        self.logger = logging.getLogger()

        if verbose:
            self.logger.setLevel(level=logging.INFO)
        else:
            self.logger.setLevel(level=logging.ERROR)

        # 控制台输出
        self.console_to_var = None
        if capture_console:
            self.console_to_var = StringIO()
            self.console_handler = logging.StreamHandler(self.console_to_var)
        else:
            self.console_handler = logging.StreamHandler()

        self.logger.addHandler(self.console_handler)

        formatter = logging.Formatter("%(asctime)s.%(msecs)03d [%(levelname)-s] %(name)s %(funcName)s : %(message)s")
        self.console_handler.setFormatter(formatter)

    def info(self, msg):
        self.logger.info(msg=msg)

    def warning(self, msg):
        self.logger.warning(msg=msg)

    def error(self, msg):
        self.logger.error(msg=msg)

    def close(self):

        if self.console_handler:
            self.console_handler.close()
        if self.logger:
            self.logger.removeHandler(self.console_handler)

    def get_console_data(self):
        if self.console_to_var:
            return self.console_to_var.getvalue()
        return ""

    def __getattr__(self, item):
        return False

if __name__ == '__main__':
    # Logger().logger.debug("sfed")

    # logger = Logger(verbose=True, capture_console=False)
    # logger.info("info")
    # logger.error("error")
    # logger.close()
    #
    # logger = Logger(verbose=False, capture_console=False)
    # logger.info("info")
    # logger.error("error")
    # logger.close()

    logger = Logger(verbose=True, capture_console=True)
    logger.info("info")
    logger.error("error")
    print(logger.get_console_data())
    logger.close()

    # logger = Logger(verbose=False, capture_console=True)
    # logger.info("info")
    # logger.error("error")
    # print(logger.get_console_data())
    # logger.close()













