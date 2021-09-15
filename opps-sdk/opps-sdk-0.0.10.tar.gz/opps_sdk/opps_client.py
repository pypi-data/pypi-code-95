from opps_sdk.core import log_util

from opps_sdk.module.mer_config import MerConfig
from fishbase.fish_logger import set_log_file, set_log_stdout


class OppsClient(object):
    connect_timeout = 15  # 网络请求超时时间
    mer_config: MerConfig  # 商户配置信息

    # sdk 版本
    __version__ = '0.0.10'

    @classmethod
    def init_log(cls, console_enable=False, log_level='', log_tag='{opps-sdk}', log_file_path=''):
        """
        初始化日志输出
        :param log_tag:
        :param log_level:
        :param console_enable: 是否在控台输出日志
        :param log_file_path:
        :return:
        """
        if console_enable:
            set_log_stdout()
        if log_file_path:
            set_log_file(log_file_path)
        if log_level:
            log_util.log_level = log_level
            if log_tag:
                log_util.log_tag = log_tag
