import logging

import os
import platform

from urllib.parse import urlsplit
from django.utils import translation
from django.shortcuts import redirect
# from django.views.generic import TemplateView

logger = logging.getLogger('django_sso_app.backend')

CURRENT_DIR = os.getcwd()


if platform.system() == 'Windows':
    def local_space_available(dir):
        """Return space available on local filesystem."""
        import ctypes
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dir), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
else:
    def local_space_available(dir):
        destination_stats = os.statvfs(dir)
        return destination_stats.f_bsize * destination_stats.f_bavail


def set_language_from_url(request, user_language):
    prev_lang = request.session.get(translation.LANGUAGE_SESSION_KEY, request.LANGUAGE_CODE)

    translation.activate(user_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language

    url = request.META.get('HTTP_REFERER', '/')
    parsed = urlsplit(url)

    _url = parsed.path
    if len(_url) > 1:
        _url = '/{}/'.format(user_language) + _url.lstrip('/{}/'.format(prev_lang))

    return redirect(_url)
