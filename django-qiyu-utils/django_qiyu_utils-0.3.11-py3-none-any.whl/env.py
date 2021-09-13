import os
import sys
from typing import Optional

__all__ = ["EnvHelper"]


class EnvKeys(object):
    """
    所有支持的 环境变量 名称
    """

    django_prod = "DJANGO_PROD"  # 如果存在这个环境变量, 则认为是在 生产 环境运行
    django_test = "DJANGO_TEST"  # 如果存在这个环境变量, 则认为是在 测试 环境运行
    django_dev = "DJANGO_DEV"  # 如果存在这个环境变量, 则认为是在 开发 环境运行


class EnvHelper(object):
    """
    当前运行环境的辅助类
    """

    @staticmethod
    def in_prod() -> bool:
        """
        是否运行在线上环境
        """
        return EnvHelper._check_env_exists(EnvKeys.django_prod)

    @staticmethod
    def in_test() -> bool:
        """
        是否运行在测试环境
        """
        return EnvHelper._check_env_exists(EnvKeys.django_test)

    @staticmethod
    def in_dev() -> bool:
        """
        是否运行在开发环境
        """
        return EnvHelper._check_env_exists(EnvKeys.django_dev)

    @staticmethod
    def _check_env_exists(key: str) -> bool:
        if os.getenv(key, None) is None:
            return False
        return True

    @staticmethod
    def try_get_from_env(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        从环境变量中获取配置 [有可能返回为 None]
        :param key: 环境变量的 key
        :param default: 默认值
        """
        return os.environ.get(key, default)

    @staticmethod
    def get_from_env(key: str, default: Optional[str] = None) -> str:
        """
        获取环境变量的值 [环境变量必须存在,否则退出进程]
        :param key: 环境变量的 key
        :param default: 默认值
        """
        value = EnvHelper.try_get_from_env(key, default)
        if value is not None:
            return value
        print(f"环境变量: {key} 没有设置, 启动服务器失败", file=sys.stderr)
        sys.exit(2)
