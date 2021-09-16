import base64
import json
from collections import Mapping
from functools import wraps
from typing import Optional, Dict

from box import Box


def normalize_gql(field: str) -> Optional[str]:
    if field:
        return field.replace('_', '-').lower()


def read_as_base64(path: str) -> bytes:
    with open(path, 'rb') as fp:
        return base64.b64encode(fp.read())


def struct_match(s1: Dict, s2: Dict) -> bool:
    return json.dumps(s1, sort_keys=True) == json.dumps(s2, sort_keys=True)


def boxify(func):
    """
    Convenience decorator to convert a dict into Box for ease of use.
    """

    @wraps(func)
    def _impl(self, *args, **kwargs):
        dict_ = func(self, *args, **kwargs)
        if dict_ and isinstance(dict_, Mapping):
            return Box(dict_)
        return dict_

    return _impl