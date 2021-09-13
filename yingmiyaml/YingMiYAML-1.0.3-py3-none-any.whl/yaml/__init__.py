# coding=utf8
# @Created : 2021/6/24 12:08 下午
# @Author  : liuyf@yingmi.cn
import sys
from yingmi.yaml.nested_dict_value import get_dict_value as get_nested_dict_value, dict_update as nested_dict_update
from yingmi.yaml import yaml_parse


def get_yaml_config(file_path: str, profile: str = None) -> object:
    """
    获取指定配置
    :param file_path: yaml配置文件路径
    :param profile: 可选，指定读取profile
    :return:
    """
    yaml = YAML(file_path)
    return yaml.get_profile(profile)


class YAML:
    """
    yaml解析辅助类
    """

    def __init__(self, file_path: str):
        self.cmd_profile = None
        self.file_path = file_path
        if len(sys.argv) > 1:
            self._parse_cmd_args()
        self.yaml_dict = yaml_parse.parse_yaml(self.file_path)

    def get_profile(self, env: str = None) -> dict:
        """
        获取指定profile
        :param env: profile名称
        :return:
        """
        if env is None and self.cmd_profile is not None:
            env = self.cmd_profile
        return YAMLConfig(yaml_parse.get_env_profile(self.yaml_dict, env))

    def _parse_cmd_args(self):
        """
        解析命令行参数
        :return:
        """
        import argparse
        parser = argparse.ArgumentParser(description='profile参数')
        # type是要传入的参数的数据类型  help是该参数的提示信息
        parser.add_argument('--profile', default=None, type=str, help='激活配置profile')

        args, _ = parser.parse_known_args()
        if 'profile' in args and args.profile is not None:
            self.cmd_profile = args.profile


class YAMLConfig(dict):
    """
    类似dict的配置包装类，支持多级key访问，比如 config['mysql.host']

    >>> config = YAMLConfigItem({'app': {'name': 'spark-kyc', 'profile': {'active': 'prod'}, 'server': {'port': 80}}})
    >>> config['app.profile.active'] == 'prod'
    True
    >>> config.get('app.server.port')
    80
    """

    def __getitem__(self, key: str):
        if key in self:
            return super().__getitem__(key)
        else:
            if '.' in key:
                return get_nested_dict_value(self, key)
        return None

    def get(self, key):
        value = self.__getitem__(key)
        if value is None:
            value = super().get(key)
        return value
