from ....tools._common import urljoin
from ....tools._datetime import cfs_datetime_adapter
import os


def _convert_name(name):
    """convert names to query parameters names
    example: fileset_id -> filesetId"""
    if "_" not in name:
        return name
    result = name.replace("_", " ").title().replace(" ", "")
    result = result[0].lower() + result[1:]
    return result


def _get_query_params(**kwargs):
    _query_parameters = []
    for (key, value) in kwargs.items():
        if value is not None:
            _query_parameters.append((_convert_name(key), value))
    return _query_parameters


def _get_url(config, endpoint):
    base_url = config.get_str("url")
    endpoint_url = config.get_str(f"endpoints.{endpoint}")
    _url = urljoin(base_url, endpoint_url)
    return _url


def _get_query_parameter(url, param):
    result = None
    if url:
        _url = url.split("?")[-1].split("&")
        params = dict((i.split("=") for i in _url))
        result = params.get(param, None)
    return result


def _convert_date_time(value):
    if value is None:
        return None
    return cfs_datetime_adapter.get_str(value)


def path_join(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)


def create_dirs_if_no_exists(folder):
    if not folder:
        return

    if not os.path.exists(folder):
        os.makedirs(folder)
