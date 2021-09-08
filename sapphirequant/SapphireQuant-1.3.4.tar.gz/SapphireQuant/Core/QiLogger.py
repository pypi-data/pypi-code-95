import logging
import os


def create_log(log_dir=None, log_name=None):
    """

    :param log_dir:
    :param log_name:
    :return:
    """
    if log_dir is None:
        log_dir = "log_dir"

    path = os.path.join(os.path.abspath("."), log_dir)

    if not os.path.exists(path):
        os.makedirs(path)
        print('创建日志目录:{0}'.format(path))

    logger = logging.getLogger(log_name)
    # 配置日志信息
    if log_name is None:
        log_name = "demo.log"
    log_name = os.path.join(path, log_name)

    # 创建一个日志 logger 实例
    logger.setLevel(logging.DEBUG)  # 设置日志级别为 DEBUG， 覆盖掉默认的日志级别 Warning

    # 创建一个 handler，用于写入日志文件， handler 可以把日志写到不同的地方
    print('创建日志文件:{0}'.format(log_name))
    fh = logging.FileHandler(log_name, "w+", encoding="utf-8")  # 将日志写在文件中
    fh.setLevel(logging.DEBUG)  # 设置日志的级别为  INFO

    # 再创建一个 handler, 用于输出控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)  # 设置日志的级别为 INFO

    # 定义handler的格式输出
    log_format = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s - %(name)s - %(message)s")  # 时间，文件名称，日志级别， 日志器名称， 字段信息

    fh.setFormatter(log_format)  # handler 加载设置的格式输出
    ch.setFormatter(log_format)  # handler 加载设置的格式输出

    # 为 logger 添加handler
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

