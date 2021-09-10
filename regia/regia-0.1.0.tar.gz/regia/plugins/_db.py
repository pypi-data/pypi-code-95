from functools import wraps
from django.conf import settings
from regia.exceptions import ConfigException


def ensure_databases(func):
    """
    确保数据库配置信息正常
    prepare database
    默认的配置需要一个default的instance
    对外屏蔽这一层
    :param func: 数据库连接函数
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        databases: dict = getattr(settings, 'DATABASES', None)
        # 判断是否为空
        if not databases:
            raise ConfigException('`DATABASES` is required')
        if databases.get('default') is None:
            raise ConfigException('`DATABASES` must have a `default` key')
        return func(*args, **kwargs)

    return wrapper
