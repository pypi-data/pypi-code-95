# -*- coding: utf-8 -*-
# @Time    : 2019-08-28 16:20
# @Author  : xzr
# @File    : __init__
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 正式环境 settings 基本设置


# SECURITY WARNING: don't run with debug turned on in production!

import logging
import os

DEBUG = False

from django.conf import settings
from decouple import config

logging.info('This env is production,DEBUG = %s' % DEBUG)
logging.info('BASE_DIR: %s' % settings.BASE_DIR)

REDIS_URL = config('REDIS_URL', default='redis://:123456@redis:6379')

DATABASES = {
        'default': {
                'ENGINE'  : 'django.db.backends.mysql',
                'NAME'    : 'djmyadmin',
                'USER'    : 'root',
                'PASSWORD': '123456',
                'HOST'    : '10.19.200.185',
                'PORT'    : '3306',
                'OPTIONS' : {'isolation_level': None, 'charset': 'utf8mb4'}
        },
        'read'   : {
                'ENGINE'  : 'django.db.backends.mysql',
                'NAME'    : 'djmyadmin',
                'USER'    : 'root',
                'PASSWORD': '123456',
                'HOST'    : '10.19.200.185',
                'PORT'    : '3306',
                'OPTIONS' : {'isolation_level': None, 'charset': 'utf8mb4'}
        },
        'write'  : {
                'ENGINE'  : 'django.db.backends.mysql',
                'NAME'    : 'djmyadmin',
                'USER'    : 'root',
                'PASSWORD': '123456',
                'HOST'    : '10.19.200.185',
                'PORT'    : '3306',
                'OPTIONS' : {'isolation_level': None, 'charset': 'utf8mb4'}
        }

}
DATABASES['read'] = DATABASES['default']
DATABASES['write'] = DATABASES['default']
DATABASES['db'] = DATABASES['default']

# session引擎设置
# SESSION_ENGINE='django.contrib.sessions.backends.cache'
# SESSION_COOKIE_AGE = 60 * 30  # 30分钟
# SESSION_SAVE_EVERY_REQUEST = True
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 关闭浏览器，则COOKIE失效
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CELERY_BROKER_URL = 'redis://:123456@h29:6379/1'

CHANNEL_LAYERS = {
        "default": {
                "BACKEND": "channels_redis.core.RedisChannelLayer",
                "CONFIG" : {
                          "hosts": [f"{REDIS_URL}/3"],
                },
        },
}


_SETTINGS_LOADER_ETCD = dict(host='localhost', port=2379,
                             ca_cert=None, cert_key=None, cert_cert=None, timeout=None,
                             user=None, password=None, grpc_options=None,
                             prefix_key=os.environ.get('DJANGO_ENV', 'dev'))

_SETTINGS_LOADER_REDIS = dict(url=f"{REDIS_URL}/4", decode_responses=True, socket_connect_timeout=3,
                              prefix_key=os.environ.get('DJANGO_ENV', 'dev'))

