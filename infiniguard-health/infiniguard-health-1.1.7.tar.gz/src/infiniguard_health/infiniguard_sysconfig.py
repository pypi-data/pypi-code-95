import json

from logging import getLogger

_logger = getLogger(__name__)

SYSCONFIG_PATH = '/etc/sysconfig/infiniguard'


def get_sku_from_iguard_sysconfig():
    return read_key_from_sysconfig_json('DDE_SKU', swallow_exceptions=True)


def get_lab_mode_from_iguard_sysconfig():
    return read_key_from_sysconfig_json('LAB_MODE', allow_missing_key=True)


def read_key_from_sysconfig_json(key, allow_missing_key=False, swallow_exceptions=False):
    """
    Reads given key from /etc/sysconfig/infiniguard.
    If allow_missing_key is True, returns None if the key does not exist.
    if swallow_exceptions is True, does not raise exceptions regarding the sysconfig file being malformed or
    inaccessible, and returns None instead.
    """
    try:
        try:
            with open(SYSCONFIG_PATH) as f:
                sysconfig_json = json.load(f)
            return sysconfig_json[key]
        except KeyError:
            if allow_missing_key:
                return None
            else:
                raise
    except (OSError, json.JSONDecodeError, KeyError):
        _logger.exception(f'Failed to read {key} from {SYSCONFIG_PATH}')
        if swallow_exceptions:
            return None
        else:
            raise

