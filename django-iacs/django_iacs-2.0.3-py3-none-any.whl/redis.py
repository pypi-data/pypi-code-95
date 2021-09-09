import redis
from django.conf import settings

__author__ = 'lee'

REDIS_CONNECTION_POOL = redis.ConnectionPool(host=settings.IACS_SETTINGS["REDIS_IP"],
                                             port=settings.IACS_SETTINGS["REDIS_PORT"],
                                             password=settings.IACS_SETTINGS["REDIS_PASSWORD"],
                                             db=0)


def check(conn, key, value):
    """
    对比value与服务器上的value是否一致

    :param conn:
    :param key:
    :param value:
    :return: boolean
    """
    try:
        redis_value = str(conn.get(key), "utf-8")
        return True if redis_value == value else False
    except TypeError:
        return False
