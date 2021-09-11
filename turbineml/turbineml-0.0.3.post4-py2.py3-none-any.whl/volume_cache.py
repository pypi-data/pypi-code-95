import os

def _get_cache_dir():
    return os.path.join(os.path.expanduser("~"), ".turbineml", "volume_cache")

def init_cache():
    cache_dir = _get_cache_dir()
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

def file_exists(digest):
    return os.path.exists(get_path(digest))

def get_path(digest):
    return os.path.join(_get_cache_dir(), digest)
