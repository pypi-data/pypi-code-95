#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging
import os
import time

from edukit_sdk.edukit.common.constant.common_constant import CommonConstant


def debug():
    return logging.DEBUG


def info():
    return logging.INFO


def warning():
    return logging.WARNING


def error():
    return logging.ERROR


def critical():
    return logging.CRITICAL


class Logger:
    _output = '[%(asctime)s] %(filename)s[line:%(lineno)d] ' \
              '%(levelname)s:%(message)s'
    _log_path = os.path.join(CommonConstant.ROOT_PATH, CommonConstant.LOG_DIR)

    @staticmethod
    def get_logger(fh_level=info(),
                   ch_level=info(),
                   formatter=_output,
                   logfile=_log_path,
                   mode='a+'):
        """
        获取logger
        :param fh_level: 输出到file中的log的日志级别,默认为info
        :param ch_level: 输出到控制台中的log的日志级别,默认为info
        :param formatter: 输入的日志格式
        :param logfile: 日志路径,默认为_log_path
        :param mode: 日志文件的读写模式
        :return:
        """
        if not os.path.exists(logfile):
            os.makedirs(logfile)
        log_path = os.path.join(logfile, time.strftime('%Y%m%d') + '.log')

        logger = logging.getLogger()
        logger.setLevel(fh_level)

        fh = logging.FileHandler(log_path, mode)
        fh.setLevel(fh_level)  # 设置输出到file中的log的日志级别

        ch = logging.StreamHandler()
        ch.setLevel(ch_level)  # 设置输出到控制台中的log的日志级别

        formatter = logging.Formatter(formatter, datefmt='%Y-%m-%d %H:%I:%S')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger
