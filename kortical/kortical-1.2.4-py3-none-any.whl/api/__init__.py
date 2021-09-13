
from kortical.api import _api


def init(url, credentials=None):
    return _api.init(url, credentials)


def get(url, *args, throw=True, **kwargs):
    kwargs['throw'] = throw
    return _api.get(url, *args, **kwargs)


def post(url, *args, throw=True, **kwargs):
    kwargs['throw'] = throw
    return _api.post(url, *args, **kwargs)