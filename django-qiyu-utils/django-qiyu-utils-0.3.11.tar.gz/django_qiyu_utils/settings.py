"""
使用方式:

在配置文件中:
```python
from django_qiyu_utils.settings import *
```
"""

import inspect
import os

from django.urls import path
from django.views.static import serve

from .env import EnvHelper

# 只需要导出有用的变量
#
# Django 项目导出的配置项
#
__all__ = [
    "DEBUG",  # by env
    "SECRET_KEY",  # by env
    "ALLOWED_HOSTS",  # by env
    "LANGUAGE_CODE",  # by env
    "TIME_ZONE",  # by env
    "USE_TZ",  # always open
    "MEDIA_URL",  # by env
    "MEDIA_ROOT",  # by env
    "STATIC_URL",  # by env
    "STATIC_ROOT",  # by env
    "STATICFILES_DIRS",
    # 静态文件服务
    "SERVE_FILE_URLS",  # by env
]

# 安全警告: 请不要在线上环境打开 DEBUG
DEBUG = False  # 防御性编程 默认不打开 DEBUG
# 只有设置了 DJANGO_DEV|DJANGO_TEST 环境变量, 才打开 DEBUG
if EnvHelper.in_dev() or EnvHelper.in_test():
    DEBUG = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/
#
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY", "wr*dd-zawlb)xpzw!hi-jbkene_^sb7oqs4_(e7Tz8yklz49_v"
)

#
# 允许访问的 HOSTS 列表
ALLOWED_HOSTS = ["*"]
# 多个域名使用 ';' 分隔
hosts = os.getenv("DJANGO_ALLOWED_HOSTS", None)
if isinstance(hosts, str) and hosts != "":
    ALLOWED_HOSTS = hosts.split(";")
##########################################################

LANGUAGE_CODE = os.getenv("DJANGO_LANGUAGE_CODE", "zh-Hans")

TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "Asia/Shanghai")

USE_TZ = True

MEDIA_URL = os.getenv("DJANGO_MEDIA_URL", "media/")

STATIC_URL = os.getenv("DJANGO_STATIC_URL", "static/")

#################################################################################
# this is ugly hack
frame = inspect.currentframe()
BASE_DIR = os.path.normpath(
    os.path.abspath(os.path.dirname(inspect.getfile(frame.f_back)))
)

MEDIA_ROOT = os.path.normpath(
    os.getenv("DJANGO_MEDIA_ROOT", os.path.join(BASE_DIR, "..", "media"))
)
STATIC_ROOT = os.path.normpath(
    os.getenv("DJANGO_STATIC_ROOT", os.path.join(BASE_DIR, "..", "static"))
)

STATICFILES_DIRS = []
if DEBUG:
    STATICFILES_DIRS = [STATIC_ROOT]
    # this do fix the problem
    # ?: (staticfiles.E002) The STATICFILES_DIRS setting
    # should not contain the STATIC_ROOT setting.
    STATIC_ROOT = None
#################################################################################


#################################################################################
# 静态文件服务 url
#
# 友情提示:
# 如果您的网站访问量比较大，那么应该使用 Web 服务器来托管静态文件
# 如果你的网站访问量非常大，那么应该使用 CDN 来托管静态文件
#
SERVE_FILE_URLS = []
# django serve static files
static_file_path = os.getenv("DJANGO_SERVE_STATIC_FILES", None)
if static_file_path is not None:
    SERVE_FILE_URLS += [
        path(f"{STATIC_URL}<path:path>", serve, {"document_root": static_file_path})
    ]

# django serve media files
media_file_path = os.getenv("DJANGO_SERVE_MEDIA_FILES", None)
if media_file_path is not None:
    SERVE_FILE_URLS += [
        path(f"{MEDIA_URL}<path:path>", serve, {"document_root": media_file_path})
    ]
#################################################################################
